"""
Generate simulated SaaS product data for feature adoption analytics.

Simulates a social media management tool (like Hootsuite) with ~2,000 users.
A new "AI Caption Generator" feature launches on 2025-06-01.

Outputs:
  - raw/users.csv               — User profiles and plan tiers
  - raw/subscriptions.csv       — Subscription lifecycle events
  - raw/product_events.csv      — User activity logs
  - raw/feature_exposures.csv   — AI Caption Generator exposure & usage
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Constants ---

NUM_USERS = 2000
DATE_START = datetime(2025, 1, 1)
DATE_END = datetime(2025, 12, 31)
FEATURE_LAUNCH = datetime(2025, 6, 1)  # AI Caption Generator launch date

PLANS = {
    "free":       {"price": 0,   "weight": 0.45},
    "pro":        {"price": 49,  "weight": 0.35},
    "enterprise": {"price": 149, "weight": 0.20},
}

# Core platform actions (pre-existing features)
PLATFORM_ACTIONS = [
    "login", "post_create", "post_schedule", "analytics_view",
    "media_upload", "team_manage", "inbox_reply", "report_export",
]

INDUSTRIES = [
    "Marketing Agency", "E-commerce", "SaaS", "Media",
    "Non-profit", "Education", "Healthcare", "Finance",
]

COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]

COUNTRIES = ["US", "CA", "GB", "AU", "DE", "FR", "BR", "IN"]


def random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between start and end."""
    delta = end - start
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return start
    return start + timedelta(seconds=random.randint(0, seconds))


# ============================================================
# 1. Users
# ============================================================

def generate_users() -> pd.DataFrame:
    """Generate user profiles with company info and plan tier."""
    records = []
    plan_names = list(PLANS.keys())
    plan_weights = [PLANS[p]["weight"] for p in plan_names]

    for i in range(1, NUM_USERS + 1):
        # Most users signed up before feature launch (existing user base)
        if random.random() < 0.7:
            signup_date = random_date(DATE_START, FEATURE_LAUNCH - timedelta(days=1))
        else:
            signup_date = random_date(DATE_START, DATE_END)

        plan = random.choices(plan_names, weights=plan_weights, k=1)[0]

        records.append({
            "user_id": f"user_{i:05d}",
            "email": fake.email(),
            "full_name": fake.name(),
            "company_name": fake.company(),
            "industry": random.choice(INDUSTRIES),
            "company_size": random.choice(COMPANY_SIZES),
            "country": random.choice(COUNTRIES),
            "plan": plan,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(records)

    # Data quality issues (realistic)
    # ~1.5% missing signup_date
    for idx in random.sample(range(len(df)), int(len(df) * 0.015)):
        df.at[idx, "signup_date"] = None
    # ~2% uppercase emails
    for idx in random.sample(range(len(df)), int(len(df) * 0.02)):
        df.at[idx, "email"] = df.at[idx, "email"].upper()
    # ~1% missing company_name
    for idx in random.sample(range(len(df)), int(len(df) * 0.01)):
        df.at[idx, "company_name"] = None

    return df


# ============================================================
# 2. Subscriptions
# ============================================================

def generate_subscriptions(users: pd.DataFrame) -> pd.DataFrame:
    """Generate subscription lifecycle events."""
    records = []

    for _, user in users.iterrows():
        if pd.isna(user["signup_date"]):
            continue

        signup = datetime.strptime(str(user["signup_date"]), "%Y-%m-%d")
        current_plan = user["plan"]

        # Initial subscription creation
        records.append({
            "subscription_id": f"sub_{fake.unique.random_number(digits=8)}",
            "user_id": user["user_id"],
            "event_type": "created",
            "plan": current_plan,
            "mrr": PLANS[current_plan]["price"],
            "event_date": signup.strftime("%Y-%m-%d"),
        })

        # Simulate lifecycle changes
        current_date = signup
        while current_date < DATE_END:
            current_date += timedelta(days=random.randint(30, 120))
            if current_date > DATE_END:
                break

            roll = random.random()
            if current_plan == "free":
                if roll < 0.06:
                    current_plan = "pro"
                    event_type = "upgraded"
                else:
                    continue
            elif current_plan == "pro":
                if roll < 0.04:
                    current_plan = "enterprise"
                    event_type = "upgraded"
                elif roll < 0.08:
                    current_plan = "free"
                    event_type = "downgraded"
                elif roll < 0.12:
                    event_type = "cancelled"
                else:
                    continue
            else:  # enterprise
                if roll < 0.03:
                    current_plan = "pro"
                    event_type = "downgraded"
                elif roll < 0.05:
                    event_type = "cancelled"
                else:
                    continue

            records.append({
                "subscription_id": f"sub_{fake.unique.random_number(digits=8)}",
                "user_id": user["user_id"],
                "event_type": event_type,
                "plan": current_plan,
                "mrr": PLANS[current_plan]["price"] if event_type != "cancelled" else 0,
                "event_date": current_date.strftime("%Y-%m-%d"),
            })

            if event_type == "cancelled":
                break

    return pd.DataFrame(records)


# ============================================================
# 3. Product Events
# ============================================================

def generate_events(users: pd.DataFrame) -> pd.DataFrame:
    """Generate user activity events for core platform features."""
    records = []

    for _, user in users.iterrows():
        if pd.isna(user["signup_date"]):
            continue

        signup = datetime.strptime(str(user["signup_date"]), "%Y-%m-%d")
        # Each user has an engagement level that stays roughly consistent
        engagement = random.uniform(0.1, 1.0)
        events_per_month = int(engagement * 25)

        current_month = signup.replace(day=1)
        while current_month <= DATE_END:
            # Some monthly variation
            n_events = max(1, int(events_per_month * random.uniform(0.5, 1.5)))

            for _ in range(n_events):
                range_start = max(current_month, signup)
                range_end = min(current_month + timedelta(days=29), DATE_END)
                if range_start >= range_end:
                    continue

                event_date = random_date(range_start, range_end)
                action = random.choices(
                    PLATFORM_ACTIONS,
                    weights=[0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.05],
                    k=1,
                )[0]

                records.append({
                    "event_id": f"evt_{fake.unique.random_number(digits=12)}",
                    "user_id": user["user_id"],
                    "event_type": action,
                    "event_timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": f"sess_{random.randint(100000, 999999)}",
                    "platform": random.choice(["web", "mobile_ios", "mobile_android"]),
                })

            current_month += timedelta(days=30)

    return pd.DataFrame(records)


# ============================================================
# 4. Feature Exposures (AI Caption Generator)
# ============================================================

def generate_feature_exposures(users: pd.DataFrame) -> pd.DataFrame:
    """
    Generate AI Caption Generator exposure and usage events.

    Only generates data AFTER the feature launch date (2025-06-01).
    Models a realistic adoption funnel:
      - ~70% of active users get exposed (see the feature)
      - ~40% of exposed users try it at least once
      - ~50% of those who try become repeat users
    Pro/Enterprise users have higher adoption rates.
    """
    records = []

    for _, user in users.iterrows():
        if pd.isna(user["signup_date"]):
            continue

        signup = datetime.strptime(str(user["signup_date"]), "%Y-%m-%d")

        # User must be signed up before or during the analysis period
        activity_start = max(signup, FEATURE_LAUNCH)
        if activity_start >= DATE_END:
            continue

        plan = user["plan"]
        # Plan-based multiplier for adoption likelihood
        plan_boost = {"free": 1.0, "pro": 1.4, "enterprise": 1.6}.get(plan, 1.0)

        # Step 1: Exposure — did the user see the feature?
        exposure_chance = 0.70 * min(plan_boost, 1.0)  # Cap at 1.0 for exposure
        if random.random() > exposure_chance:
            continue  # Not exposed

        # When were they first exposed?
        # Most exposures happen within first 2 months of launch
        days_to_expose = int(random.expovariate(1 / 20))  # Mean ~20 days
        exposure_date = FEATURE_LAUNCH + timedelta(days=days_to_expose)
        exposure_date = max(exposure_date, activity_start)
        if exposure_date >= DATE_END:
            continue

        records.append({
            "exposure_id": f"exp_{fake.unique.random_number(digits=10)}",
            "user_id": user["user_id"],
            "event_type": "exposed",
            "event_timestamp": exposure_date.strftime("%Y-%m-%d %H:%M:%S"),
            "feature_name": "ai_caption_generator",
            "context": random.choice([
                "dashboard_banner", "post_composer_tooltip",
                "feature_announcement_email", "in_app_notification",
            ]),
        })

        # Step 2: First use — did they try the feature?
        adopt_chance = 0.40 * plan_boost
        if random.random() > min(adopt_chance, 0.85):
            continue  # Exposed but never used

        # Time to adopt: days from exposure to first use
        days_to_adopt = int(random.expovariate(1 / 10))  # Mean ~10 days
        first_use_date = exposure_date + timedelta(days=max(days_to_adopt, 1))
        if first_use_date >= DATE_END:
            continue

        records.append({
            "exposure_id": f"exp_{fake.unique.random_number(digits=10)}",
            "user_id": user["user_id"],
            "event_type": "first_use",
            "event_timestamp": first_use_date.strftime("%Y-%m-%d %H:%M:%S"),
            "feature_name": "ai_caption_generator",
            "context": random.choice([
                "post_composer", "bulk_schedule", "content_calendar",
            ]),
        })

        # Step 3: Repeat usage — did they keep using it?
        repeat_chance = 0.50 * plan_boost
        if random.random() > min(repeat_chance, 0.80):
            continue  # One-time user

        # Generate repeat usage events
        usage_date = first_use_date
        usage_frequency = random.uniform(2, 15)  # Days between uses

        while usage_date < DATE_END:
            usage_date += timedelta(days=int(random.expovariate(1 / usage_frequency)))
            if usage_date >= DATE_END:
                break

            records.append({
                "exposure_id": f"exp_{fake.unique.random_number(digits=10)}",
                "user_id": user["user_id"],
                "event_type": "repeat_use",
                "event_timestamp": usage_date.strftime("%Y-%m-%d %H:%M:%S"),
                "feature_name": "ai_caption_generator",
                "context": random.choice([
                    "post_composer", "bulk_schedule",
                    "content_calendar", "quick_action",
                ]),
            })

    return pd.DataFrame(records)


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 50)
    print("SaaS Feature Adoption Data Generator")
    print("=" * 50)

    print("\n1. Generating users...")
    users = generate_users()
    users.to_csv(os.path.join(OUTPUT_DIR, "users.csv"), index=False)
    print(f"   → {len(users)} users")

    print("2. Generating subscriptions...")
    subscriptions = generate_subscriptions(users)
    subscriptions.to_csv(os.path.join(OUTPUT_DIR, "subscriptions.csv"), index=False)
    print(f"   → {len(subscriptions)} subscription events")

    print("3. Generating product events...")
    events = generate_events(users)
    events.to_csv(os.path.join(OUTPUT_DIR, "product_events.csv"), index=False)
    print(f"   → {len(events)} events")

    print("4. Generating feature exposures (AI Caption Generator)...")
    exposures = generate_feature_exposures(users)
    exposures.to_csv(os.path.join(OUTPUT_DIR, "feature_exposures.csv"), index=False)
    print(f"   → {len(exposures)} exposure/usage events")

    # Summary stats
    if len(exposures) > 0:
        exposed = exposures[exposures["event_type"] == "exposed"]["user_id"].nunique()
        first_use = exposures[exposures["event_type"] == "first_use"]["user_id"].nunique()
        repeat = exposures[exposures["event_type"] == "repeat_use"]["user_id"].nunique()
        print(f"\n   Funnel: {exposed} exposed → {first_use} first use → {repeat} repeat users")

    print(f"\nAll files saved to {OUTPUT_DIR}/")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f} ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
