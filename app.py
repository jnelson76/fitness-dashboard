from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "log.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"daily_logs": [], "weight_log": [], "workout_log": []}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Program data
# ---------------------------------------------------------------------------

PROFILE = {
    "age": 49,
    "height": "6'2\"",
    "weight": 193,
    "goal": "Lean Bulk - Build Muscle",
    "calories": 2600,
    "protein": 190,
    "carbs": 260,
    "fat": 87,
}

SUPPLEMENTS = [
    {"name": "Omega-3 / Fish Oil", "dose": "2,000 mg", "when": "With 1st meal"},
    {"name": "Vitamin D3", "dose": "2,000-5,000 IU", "when": "With 1st meal"},
    {"name": "Creatine Monohydrate", "dose": "5g", "when": "Any time daily"},
    {"name": "Electrolytes", "dose": "1-2 servings", "when": "During/after training"},
    {"name": "Protein Powder (Whey Isolate)", "dose": "As needed to hit 190g", "when": "Post-workout or between meals"},
]

MEAL_PLAN = {
    "overview": {
        "calories": 2600,
        "protein": 190,
        "carbs": 260,
        "fat": 87,
        "notes": [
            "1g protein per lb bodyweight for muscle building",
            "Slight caloric surplus (~300-500 above maintenance) to fuel growth",
            "Green vegetables are UNLIMITED - don't count their calories",
            "Drink a gallon of water daily with electrolytes",
            "Always consume protein after training",
            "Cook with butter, olive oil, avocado oil, or ghee",
        ],
    },
    "meals": [
        {
            "name": "Meal 1 - Breakfast",
            "time": "~8:00 AM",
            "foods": [
                {"food": "3 whole eggs + 1 cup egg whites", "protein": 43, "cals": 350},
                {"food": "1 tbsp butter (cook eggs in)", "protein": 0, "cals": 100},
                {"food": "2 slices bacon or sausage patty", "protein": 10, "cals": 160},
                {"food": "1 cup cooked green veggies", "protein": 0, "cals": 0},
            ],
            "total_protein": 53,
            "total_cals": 610,
        },
        {
            "name": "Meal 2 - Lunch",
            "time": "~12:00 PM",
            "foods": [
                {"food": "8 oz chicken thighs or breast", "protein": 52, "cals": 280},
                {"food": "1 cup white rice (cooked in bone broth)", "protein": 4, "cals": 200},
                {"food": "1 tbsp olive oil or avocado oil", "protein": 0, "cals": 126},
                {"food": "Unlimited green veggies / salad", "protein": 0, "cals": 0},
            ],
            "total_protein": 56,
            "total_cals": 606,
        },
        {
            "name": "Meal 3 - Post-Workout / Snack",
            "time": "~3:30 PM",
            "foods": [
                {"food": "50g whey isolate shake (water)", "protein": 50, "cals": 236},
                {"food": "2 tbsp natural peanut butter", "protein": 8, "cals": 188},
                {"food": "1 apple or berries", "protein": 0, "cals": 80},
            ],
            "total_protein": 58,
            "total_cals": 504,
        },
        {
            "name": "Meal 4 - Dinner",
            "time": "~7:00 PM",
            "foods": [
                {"food": "8 oz ribeye steak or pork chop", "protein": 50, "cals": 500},
                {"food": "1 cup potatoes or rice", "protein": 3, "cals": 200},
                {"food": "1 tbsp butter or cooking fat", "protein": 0, "cals": 100},
                {"food": "Broccoli / carrots / green veggies", "protein": 0, "cals": 0},
            ],
            "total_protein": 53,
            "total_cals": 800,
        },
    ],
    "shopping_list": {
        "Proteins": [
            "Eggs (2-3 dozen/week)",
            "Chicken thighs or breasts (3-4 lbs)",
            "Ribeye steaks or NY strip (2-3 lbs)",
            "Ground beef 90/10 (2 lbs)",
            "Pork chops or pork loin (2 lbs)",
            "Bacon (1-2 lbs)",
            "Sausage patties (1 lb)",
            "Wild salmon (1 lb, optional swap)",
            "Whey isolate protein powder",
        ],
        "Carbs & Veggies": [
            "White rice (2-3 lbs)",
            "Potatoes (3-4 lbs)",
            "Broccoli (2 heads)",
            "Carrots (1 lb bag)",
            "Spinach / mixed greens",
            "Avocados (4-6)",
            "Berries (fresh or frozen)",
            "Apples (4-6)",
            "Oatmeal (optional breakfast swap)",
        ],
        "Fats & Pantry": [
            "Butter - unsalted (2 sticks)",
            "Extra virgin olive oil",
            "Avocado oil",
            "Natural peanut butter",
            "Bone broth (for cooking rice)",
            "Sea salt, black pepper, garlic",
            "Coffee",
        ],
        "Dairy": [
            "Cottage cheese (good brand)",
            "Icelandic yogurt / Skyr",
            "Fairlife milk",
            "Aged cheddar cheese",
            "Heavy cream (for coffee)",
        ],
    },
    "swap_options": [
        "Chicken <-> Turkey breast",
        "Ribeye <-> NY Strip <-> Pork Chop <-> Lamb Chop",
        "Ground beef <-> Ground turkey",
        "Rice <-> Potatoes <-> Oatmeal <-> Whole grain pasta",
        "Eggs <-> Cottage cheese for quick protein",
        "Any protein shake meal can be Fairlife milk + protein powder in Ninja Creami",
    ],
}


# Weekly schedule: Starting Strength A/B + Kettlebell + Cardio
WEEKLY_SCHEDULE = [
    {"day": "Sunday", "type": "rest", "label": "Rest / Light Walk"},
    {"day": "Monday", "type": "workout_a", "label": "Workout A - Squat / Bench / Deadlift"},
    {"day": "Tuesday", "type": "cardio", "label": "Cardio - 3 Mile Ruck or Walk"},
    {"day": "Wednesday", "type": "workout_b", "label": "Workout B - Squat / OHP / Deadlift"},
    {"day": "Thursday", "type": "kettlebell", "label": "Kettlebell - Clean & Press (The Giant)"},
    {"day": "Friday", "type": "workout_a", "label": "Workout A - Squat / Bench / Deadlift"},
    {"day": "Saturday", "type": "active_rest", "label": "Active Recovery / Bodyweight"},
]

WORKOUTS = {
    "workout_a": {
        "name": "Workout A",
        "duration": "45-60 min",
        "warmup": "5-10 min light movement, then empty bar 2x5, 50% work weight 1x5, 75% 1x3",
        "exercises": [
            {
                "name": "Barbell Back Squat",
                "sets": "3 x 5",
                "start": "95 lbs",
                "target": "Quads, glutes, full body",
                "notes": "Low-bar position. Hips back, chest up, full depth (hips at/below knees). Add 10 lbs/session until slow, then 5 lbs.",
                "equipment": "Olympic bar + squat rack",
            },
            {
                "name": "Barbell Bench Press",
                "sets": "3 x 5",
                "start": "65 lbs",
                "target": "Chest, triceps, shoulders",
                "notes": "Bar to mid-chest, elbows 45 degrees. Tuck shoulder blades, feet planted. Add 5 lbs/session.",
                "equipment": "Olympic bar + bench (flat)",
            },
            {
                "name": "Barbell Deadlift",
                "sets": "1 x 5",
                "start": "135 lbs",
                "target": "Posterior chain, back, grip",
                "notes": "Conventional pull. Hips back, chest up, bar over mid-foot. Reset each rep. Add 10 lbs/session, then 5 lbs.",
                "equipment": "Olympic bar",
            },
            {
                "name": "Dumbbell Curls",
                "sets": "2 x 10-15",
                "start": "25 lbs each",
                "target": "Biceps",
                "notes": "Standing, palms up, slow negatives. Go to failure on last set.",
                "equipment": "25 lb dumbbells",
            },
        ],
    },
    "workout_b": {
        "name": "Workout B",
        "duration": "45-60 min",
        "warmup": "5-10 min light movement, then empty bar 2x5, 50% work weight 1x5, 75% 1x3",
        "exercises": [
            {
                "name": "Barbell Back Squat",
                "sets": "3 x 5",
                "start": "95 lbs (progress from last session)",
                "target": "Quads, glutes, full body",
                "notes": "Same as Workout A. Consistency is key. Film yourself to check depth.",
                "equipment": "Olympic bar + squat rack",
            },
            {
                "name": "Barbell Overhead Press",
                "sets": "3 x 5",
                "start": "45 lbs",
                "target": "Shoulders, triceps, upper chest",
                "notes": "Standing strict press. Bar from chest to overhead, NO leg drive. Tight core. Add 5 lbs/session, then 2.5 lbs.",
                "equipment": "Olympic bar",
            },
            {
                "name": "Barbell Deadlift",
                "sets": "1 x 5",
                "start": "135 lbs (progress from last session)",
                "target": "Posterior chain, back, grip",
                "notes": "Reset each rep - don't bounce. Keep bar close to shins.",
                "equipment": "Olympic bar",
            },
            {
                "name": "Skull Crushers",
                "sets": "2 x 10-12",
                "start": "Empty bar or light weight",
                "target": "Triceps",
                "notes": "Lying on bench, lower bar to forehead, extend. Control the negative.",
                "equipment": "Olympic bar + bench",
            },
        ],
    },
    "kettlebell": {
        "name": "Kettlebell Day - The Giant + Pyramid Foundations",
        "duration": "30-40 min",
        "warmup": "5 min halos, arm circles, and 10 light goblet squats to warm up hips and shoulders",
        "exercises": [
            {
                "name": "Single KB Swing",
                "sets": "3 x 10-15 per side",
                "start": "125 lb kettlebell",
                "target": "Posterior chain - glutes, hamstrings, core, grip",
                "notes": "Pyramid Level 1 foundation. Hike the bell back, snap hips forward explosively, arms are just hooks. Bell should float to chest height. Do NOT squat the swing - it's a hip hinge. Reset between reps if needed at this weight.",
                "equipment": "125 lb kettlebell",
            },
            {
                "name": "Turkish Get-Up (TGU)",
                "sets": "2-3 per side (singles)",
                "start": "125 lb kettlebell (or scale down if needed)",
                "target": "Full body stability - shoulders, core, hips, legs",
                "notes": "Pyramid Level 1 foundation. Slow and controlled. Each phase is its own exercise: roll to press, to elbow, to hand, to bridge, to kneeling, to standing. Reverse it back down. Eyes on the bell the entire time. This is the #1 exercise for bulletproofing shoulders.",
                "equipment": "125 lb kettlebell",
            },
            {
                "name": "Goblet Squat",
                "sets": "3 x 8-12",
                "start": "125 lb kettlebell",
                "target": "Quads, glutes, core, upper back",
                "notes": "Pyramid Level 1 foundation. Hold bell at chest, elbows between knees at the bottom. Sit deep, drive knees out, chest up. Pause at the bottom for 1-2 seconds to build strength in the hole.",
                "equipment": "125 lb kettlebell",
            },
            {
                "name": "Single KB Clean & Press (The Giant - Geoff Neupert)",
                "sets": "AMRAP in 20 min - sets of 2-3 reps per side",
                "start": "125 lb kettlebell",
                "target": "Shoulders, back, core, legs - full body",
                "notes": "Density training: try to increase total reps within the same time frame each week. Alternate sides. Full stretch and squeeze on every rep. Rest as needed between sets but keep it under 90 seconds. This is the heart of the Geoff Neupert Giant program.",
                "equipment": "125 lb kettlebell",
            },
        ],
        "week_rotation": [
            "Week 1 (Heavy): Clean & Press sets of 2-3 reps. Heavy and explosive. Swings x10, TGU x2/side, Goblet Squat x8.",
            "Week 2 (Volume): Clean & Press sets of 5-8 reps (lighter if needed). Slow, controlled. Swings x15, TGU x3/side, Goblet Squat x12. Let lactic acid build.",
        ],
        "program_note": "Pyramid Level 1: Swing, TGU, Goblet Squat. These three movements build the foundation for all kettlebell work. Master these before progressing to Level 2 (snatch, windmill, front squat). The Giant Clean & Press by Geoff Neupert layers on top for strength and hypertrophy.",
    },
    "cardio": {
        "name": "Cardio Day",
        "duration": "30-45 min",
        "warmup": "5 min easy walking",
        "exercises": [
            {
                "name": "Ruck Walk or Brisk Walk",
                "sets": "3 miles",
                "start": "Bodyweight or light pack",
                "target": "Cardiovascular health, recovery",
                "notes": "Keep heart rate moderate. This is for health and recovery, not exhaustion. Add a weighted pack (20-30 lbs) when ready.",
                "equipment": "None (backpack optional)",
            },
        ],
    },
    "active_rest": {
        "name": "Active Recovery / Bodyweight",
        "duration": "20-30 min",
        "warmup": "5 min easy movement",
        "exercises": [
            {
                "name": "Push-ups",
                "sets": "3 sets: 5 normal + 5 wide + 5 close",
                "start": "Bodyweight",
                "target": "Chest, triceps, shoulders",
                "notes": "Controlled reps, full range of motion.",
                "equipment": "None",
            },
            {
                "name": "Air Squats",
                "sets": "2 x 50 reps",
                "start": "Bodyweight",
                "target": "Quads, glutes",
                "notes": "Full depth, control the movement.",
                "equipment": "None",
            },
            {
                "name": "Calf Raises",
                "sets": "2 x 50 reps",
                "start": "Bodyweight",
                "target": "Calves",
                "notes": "Full range - stretch at bottom, squeeze at top.",
                "equipment": "None",
            },
            {
                "name": "Standing High Knees + Butt Kicks",
                "sets": "50 each",
                "start": "Bodyweight",
                "target": "Conditioning, hip flexors, hamstrings",
                "notes": "Keep it moving, get the blood flowing.",
                "equipment": "None",
            },
        ],
    },
}

PROGRESSION_TIPS = [
    "Squat & Deadlift: Add 10 lbs per session until it slows down, then 5 lbs per session.",
    "Bench & OHP: Add 5 lbs per session, then 2.5 lbs when you stall.",
    "When you stall 3 sessions in a row, deload 10% and work back up.",
    "Focus on FULL STRETCH and SQUEEZE - how many reps doesn't matter if the muscle isn't working.",
    "Alternate heavy weeks (6-8 reps, heavy) and volume weeks (12-15 reps, controlled) every 2 weeks.",
    "Linear gains typically last 3-6 months. After that we'll switch to intermediate programming.",
    "Film your squats and deadlifts to check form. Bad form = injury.",
]

TRAINING_PRINCIPLES = [
    "Muscle grows from micro-tears repaired by amino acids - you can break a muscle in 2 hard sets.",
    "Heavy week: Warm-up set, then heavy 6-8 reps, followed by a burnout set at 50-75% weight.",
    "Volume week: 15-30 reps with full stretch and slow squeeze. Let lactic acid build up.",
    "If the muscle isn't dead after your sets, you're wasting time. Intensity > volume.",
    "Always consume protein within 1 hour after training.",
    "Rest 3-5 min between heavy compound lifts, 2-3 min between accessories.",
    "At 49, recovery is king. Sleep 7-8 hours. Don't skip rest days.",
]


@app.route("/")
def index():
    today = date.today()
    day_name = today.strftime("%A")
    today_schedule = next(
        (s for s in WEEKLY_SCHEDULE if s["day"] == day_name),
        WEEKLY_SCHEDULE[0],
    )
    today_workout = WORKOUTS.get(today_schedule["type"])

    data = load_data()
    recent_weights = sorted(data.get("weight_log", []), key=lambda x: x["date"])[-30:]

    return render_template(
        "index.html",
        profile=PROFILE,
        today=today.isoformat(),
        day_name=day_name,
        today_schedule=today_schedule,
        today_workout=today_workout,
        schedule=WEEKLY_SCHEDULE,
        workouts=WORKOUTS,
        meal_plan=MEAL_PLAN,
        supplements=SUPPLEMENTS,
        shopping_list=MEAL_PLAN["shopping_list"],
        swap_options=MEAL_PLAN["swap_options"],
        progression_tips=PROGRESSION_TIPS,
        training_principles=TRAINING_PRINCIPLES,
        recent_weights=recent_weights,
        data=data,
    )


@app.route("/api/log", methods=["POST"])
def log_entry():
    data = load_data()
    entry = request.json
    entry["timestamp"] = datetime.now().isoformat()

    if entry.get("type") == "weight":
        data["weight_log"].append(entry)
    elif entry.get("type") == "workout":
        data["workout_log"].append(entry)
    else:
        data["daily_logs"].append(entry)

    save_data(data)
    return jsonify({"status": "ok"})


@app.route("/api/data")
def get_data():
    return jsonify(load_data())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
