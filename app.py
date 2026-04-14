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


# Weekly schedule: Every day active, intensity managed
# Post-hernia recovery (Dec 2025) - no deadlifts, conservative progression
WEEKLY_SCHEDULE = [
    {"day": "Sunday", "type": "bands_walk", "label": "Band Work + Walk (5-10k steps)"},
    {"day": "Monday", "type": "workout_a", "label": "Push Day - Incline Bench / OHP"},
    {"day": "Tuesday", "type": "kettlebell", "label": "Kettlebell - Pyramid L1 + The Giant"},
    {"day": "Wednesday", "type": "workout_b", "label": "Pull Day - Rows / Curls"},
    {"day": "Thursday", "type": "walk_bands", "label": "Walk (10k steps) + Band Work"},
    {"day": "Friday", "type": "workout_c", "label": "Legs + Chest - Squats / Incline"},
    {"day": "Saturday", "type": "kettlebell_light", "label": "KB Swings + Bodyweight + Walk"},
]

DAILY_STEPS = {
    "minimum": 5000,
    "target": 10000,
    "note": "Hit 5k minimum every single day. Shoot for 10k on non-lifting days. Walking is the most underrated fat loss and health tool there is.",
}

WORKOUTS = {
    "workout_a": {
        "name": "Push Day - Chest Focus",
        "duration": "40-50 min",
        "warmup": "5 min walk or arm circles, then empty bar 2x5, 50% work weight 1x5",
        "daily": "Band pull-aparts 2x20 + 5,000 steps minimum",
        "exercises": [
            {
                "name": "Incline Barbell Bench Press",
                "sets": "3 x 8-10",
                "start": "Empty bar (45 lbs) - build up slowly post-hernia",
                "target": "Upper chest, front delts, triceps",
                "notes": "PRIMARY CHEST BUILDER. Set bench to 30-45 degree incline. Bar to upper chest, elbows 45 degrees. Tuck shoulder blades, arch slightly, feet planted. Full stretch at bottom, squeeze chest hard at top. Add 5 lbs/session when you hit 10 reps on all sets.",
                "equipment": "Olympic bar + bench (incline)",
            },
            {
                "name": "Barbell Overhead Press",
                "sets": "3 x 8-10",
                "start": "Empty bar (45 lbs)",
                "target": "Shoulders, triceps, upper chest",
                "notes": "Standing strict press. Bar from chest to overhead, NO leg drive. Tight core, squeeze glutes. Builds the shelf that makes your chest look bigger.",
                "equipment": "Olympic bar",
            },
            {
                "name": "Push-ups (Wide Grip)",
                "sets": "2 sets to failure",
                "start": "Bodyweight",
                "target": "Chest, triceps - volume finisher",
                "notes": "Hands wider than shoulder width to hit more chest. Go slow on the way down (3 seconds), explode up. If you can do 20+, elevate feet on bench.",
                "equipment": "None",
            },
            {
                "name": "Skull Crushers",
                "sets": "2 x 10-12",
                "start": "Empty bar or light weight",
                "target": "Triceps",
                "notes": "Lying on bench, lower bar to forehead, extend. Control the negative. Bigger triceps = bigger pressing numbers.",
                "equipment": "Olympic bar + bench",
            },
            {
                "name": "Band Lateral Raises",
                "sets": "2 x 15-20",
                "start": "Light-medium band",
                "target": "Side delts - shoulder width",
                "notes": "Stand on band, raise arms to shoulder height. Slow and controlled. Builds shoulder caps that frame the chest.",
                "equipment": "Resistance band",
            },
        ],
    },
    "workout_b": {
        "name": "Pull Day - Back & Biceps",
        "duration": "35-45 min",
        "warmup": "5 min walk, band pull-aparts 2x15, empty bar rows 2x8",
        "daily": "Band pull-aparts 2x20 + 5,000 steps minimum",
        "exercises": [
            {
                "name": "Barbell Row (Bent-Over)",
                "sets": "3 x 8-10",
                "start": "65 lbs - keep it light, brace core",
                "target": "Upper back, lats, rear delts",
                "notes": "REPLACES DEADLIFT for now (post-hernia). Hinge at hips ~45 degrees, pull bar to lower chest. Keep core braced but this is much less abdominal pressure than a deadlift. Squeeze shoulder blades at top.",
                "equipment": "Olympic bar",
            },
            {
                "name": "Band Face Pulls",
                "sets": "3 x 15-20",
                "start": "Medium band",
                "target": "Rear delts, rotator cuff, upper back",
                "notes": "Anchor band at face height (door frame, rack). Pull to face, elbows high, rotate hands out at the end. The #1 exercise for shoulder health and posture. Do these every day if you want.",
                "equipment": "Resistance band",
            },
            {
                "name": "Dumbbell Curls",
                "sets": "2 x 12-15",
                "start": "25 lbs each",
                "target": "Biceps",
                "notes": "Standing, palms up, slow negatives (3 sec down). Go to failure on last set.",
                "equipment": "25 lb dumbbells",
            },
            {
                "name": "Band Bicep Curls",
                "sets": "2 x 20 (burnout)",
                "start": "Light-medium band",
                "target": "Biceps - high rep pump",
                "notes": "Stand on band, curl to shoulders. Squeeze at top. High reps for blood flow and pump after the heavy curls.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Pull-Aparts",
                "sets": "2 x 20",
                "start": "Light band",
                "target": "Rear delts, upper back, posture",
                "notes": "Hold band at chest height, pull apart until band touches chest. Squeeze shoulder blades. Can do 100 of these daily for shoulder health.",
                "equipment": "Resistance band",
            },
        ],
    },
    "workout_c": {
        "name": "Legs + Extra Chest",
        "duration": "40-50 min",
        "warmup": "5 min walk, bodyweight squats 2x10, leg swings",
        "daily": "Band pull-aparts 2x20 + 5,000 steps minimum",
        "exercises": [
            {
                "name": "Air Squats / Goblet Squats",
                "sets": "3 x 15-20 (bodyweight) or 3 x 10-12 (goblet w/ 25lb KB)",
                "start": "Bodyweight - progress to KB when ready",
                "target": "Quads, glutes",
                "notes": "You're here now with air squats - that's perfect. When 20 reps feels easy, hold the 25lb KB goblet style. When THAT'S easy, move to barbell back squat with just the empty bar. No rush post-hernia. Depth and control over weight.",
                "equipment": "None / 25 lb kettlebell",
            },
            {
                "name": "Calf Raises",
                "sets": "3 x 15-20",
                "start": "Bodyweight, progress to holding KB",
                "target": "Calves",
                "notes": "Full range - deep stretch at bottom, hard squeeze at top. Hold top for 1 second. Calves respond to high reps.",
                "equipment": "Calf raise / step",
            },
            {
                "name": "Incline Dumbbell Press",
                "sets": "3 x 12-15",
                "start": "25 lbs each hand",
                "target": "Upper chest - second chest session of the week",
                "notes": "Bench at 30-45 degrees. Deeper stretch than barbell. Let dumbbells go wide at the bottom, squeeze together at top. Chest grows from frequency - hitting it twice a week is key.",
                "equipment": "25 lb dumbbells + bench (incline)",
            },
            {
                "name": "Push-ups (Close Grip)",
                "sets": "2 sets to failure",
                "start": "Bodyweight",
                "target": "Inner chest, triceps",
                "notes": "Hands shoulder width or narrower. Squeeze chest at top. Different angle than Monday's wide push-ups.",
                "equipment": "None",
            },
        ],
    },
    "kettlebell": {
        "name": "Kettlebell Day - Pyramid L1 + The Giant",
        "duration": "30-40 min",
        "warmup": "5 min halos, arm circles, and 10 light goblet squats to warm up hips and shoulders",
        "daily": "10,000 steps target today + band pull-aparts 2x20",
        "exercises": [
            {
                "name": "Two-Hand KB Swing",
                "sets": "5 x 15-20",
                "start": "25 lb kettlebell",
                "target": "Posterior chain - glutes, hamstrings, core",
                "notes": "Pyramid Level 1 foundation. Hike the bell back, snap hips forward explosively, arms are just hooks. Bell should float to chest height. This replaces deadlifts for posterior chain work - much safer post-hernia because the load is dynamic, not grinding. Do NOT squat the swing - it's a HIP HINGE.",
                "equipment": "25 lb kettlebell",
            },
            {
                "name": "Turkish Get-Up (TGU)",
                "sets": "3 per side (singles, alternating)",
                "start": "25 lb kettlebell",
                "target": "Full body stability - shoulders, core, hips, legs",
                "notes": "Pyramid Level 1 foundation. Slow and controlled - each rep should take 30-45 seconds. Roll to press, to elbow, to hand, to bridge, to kneeling, to standing. Reverse it back down. Eyes on the bell the entire time. The #1 exercise for bulletproofing shoulders and core stability.",
                "equipment": "25 lb kettlebell",
            },
            {
                "name": "Goblet Squat",
                "sets": "3 x 10-15",
                "start": "25 lb kettlebell",
                "target": "Quads, glutes, core, upper back",
                "notes": "Pyramid Level 1 foundation. Hold bell at chest (horns up), elbows between knees at the bottom. Sit deep, drive knees out, chest up. Pause at the bottom for 1-2 seconds. Great progression from air squats.",
                "equipment": "25 lb kettlebell",
            },
            {
                "name": "Single KB Clean & Press (The Giant - Geoff Neupert)",
                "sets": "AMRAP in 15-20 min - sets of 3-5 reps per side",
                "start": "25 lb kettlebell",
                "target": "Shoulders, back, core, legs - full body",
                "notes": "The heart of Geoff Neupert's Giant program. Density training: try to increase total reps within the same time frame each week. Alternate sides. Full stretch and squeeze on every rep. Rest as needed between sets but keep it under 60-90 seconds. At 25 lbs you can push the reps higher and focus on volume.",
                "equipment": "25 lb kettlebell",
            },
        ],
        "week_rotation": [
            "Week 1 (Build Volume): Clean & Press sets of 5 reps/side. Swings x20, TGU x3/side, Goblet Squat x15. Focus on accumulating reps.",
            "Week 2 (Slow & Controlled): Clean & Press sets of 3-5 reps/side with 3 sec negatives. Swings x15, TGU x3/side (extra slow), Goblet Squat x10 with pause. Let lactic acid build.",
        ],
        "program_note": "Pyramid Level 1: Swing, TGU, Goblet Squat. These three movements build the foundation for all kettlebell work. At 25 lbs, focus on PERFECT FORM and high reps. When you can do 25+ swings, 5 TGUs per side, and 20 goblet squats all without stopping, consider stepping up to a 35 lb bell. The Giant Clean & Press by Geoff Neupert layers on top for strength and hypertrophy.",
    },
    "kettlebell_light": {
        "name": "KB Swings + Bodyweight + Walk",
        "duration": "25-35 min + walking",
        "warmup": "5 min easy walk, arm circles, hip circles",
        "daily": "10,000 steps target today",
        "exercises": [
            {
                "name": "Two-Hand KB Swing",
                "sets": "10 sets of 10 (100 total swings)",
                "start": "25 lb kettlebell",
                "target": "Posterior chain, conditioning",
                "notes": "Simple & Sinister style. 10 swings, rest 30-60 sec, repeat. 100 total swings. This builds incredible hip power and conditioning without beating you up.",
                "equipment": "25 lb kettlebell",
            },
            {
                "name": "Push-ups",
                "sets": "3 sets: 5 normal + 5 wide + 5 close",
                "start": "Bodyweight",
                "target": "Chest, triceps - extra chest volume",
                "notes": "Easy chest work to keep frequency up. Don't go to failure today.",
                "equipment": "None",
            },
            {
                "name": "Air Squats",
                "sets": "2 x 50 reps",
                "start": "Bodyweight",
                "target": "Quads, glutes",
                "notes": "Full depth, controlled. This is what you're doing now - keep it up.",
                "equipment": "None",
            },
            {
                "name": "Walk / Ruck",
                "sets": "Shoot for 10,000 steps total today",
                "start": "Bodyweight, add backpack when ready",
                "target": "Cardiovascular health, recovery, fat loss",
                "notes": "Break it up if needed - morning walk + evening walk. Walking is the best recovery tool and burns more fat than you think over time.",
                "equipment": "None (backpack optional)",
            },
        ],
    },
    "bands_walk": {
        "name": "Band Work + Walking",
        "duration": "20-25 min bands + walking throughout the day",
        "warmup": "5 min easy walk",
        "daily": "10,000 steps target today",
        "exercises": [
            {
                "name": "Band Pull-Aparts",
                "sets": "3 x 20",
                "start": "Light band",
                "target": "Rear delts, upper back, posture",
                "notes": "Hold band at chest height, pull apart until band touches chest. Daily shoulder health work.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Face Pulls",
                "sets": "3 x 15",
                "start": "Medium band, anchor at face height",
                "target": "Rear delts, rotator cuff",
                "notes": "Pull to face, elbows high, rotate hands out. Protects shoulders for pressing days.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Lateral Raises",
                "sets": "3 x 15-20",
                "start": "Light band",
                "target": "Side delts - builds shoulder width",
                "notes": "Stand on band, raise arms to sides. Pause at top. Shoulders recover fast and can be trained frequently.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Tricep Pushdowns",
                "sets": "3 x 15-20",
                "start": "Medium band, anchor overhead",
                "target": "Triceps",
                "notes": "Anchor band overhead (pull-up bar, door top). Push down, squeeze at bottom. Supports your pressing days.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Bicep Curls",
                "sets": "3 x 15-20",
                "start": "Light-medium band",
                "target": "Biceps",
                "notes": "Stand on band, curl up. Light pump work - arms recover fast and grow from frequency.",
                "equipment": "Resistance band",
            },
            {
                "name": "Walk / Steps",
                "sets": "5,000 - 10,000 steps",
                "start": "Just walk",
                "target": "Cardiovascular health, recovery",
                "notes": "This is your active recovery day. Walk throughout the day - morning, lunch, evening. Podcast, music, whatever keeps you moving.",
                "equipment": "None",
            },
        ],
    },
    "walk_bands": {
        "name": "Walk Day + Band Work",
        "duration": "20 min bands + walking throughout the day",
        "warmup": "Just start walking",
        "daily": "10,000 steps target today - this is your big walking day",
        "exercises": [
            {
                "name": "Long Walk / Ruck",
                "sets": "10,000 steps (about 4-5 miles)",
                "start": "Bodyweight, add pack later",
                "target": "Cardiovascular health, fat burning, mental health",
                "notes": "Break it up: 30 min morning + 30 min evening, or one longer walk. Walking at a brisk pace burns ~100 cal/mile. At your height and weight, 10k steps is roughly 5 miles / 500 calories.",
                "equipment": "None (backpack optional)",
            },
            {
                "name": "Band Pull-Aparts",
                "sets": "3 x 20",
                "start": "Light band",
                "target": "Rear delts, posture",
                "notes": "Do these while watching TV, between meetings, wherever. 100 daily pull-aparts is a great habit.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Face Pulls",
                "sets": "3 x 15",
                "start": "Medium band",
                "target": "Rear delts, rotator cuff",
                "notes": "Keep shoulders healthy for pressing days.",
                "equipment": "Resistance band",
            },
            {
                "name": "Band Chest Flyes",
                "sets": "3 x 15-20",
                "start": "Light-medium band, anchor behind you",
                "target": "Chest - light pump to maintain frequency",
                "notes": "Anchor band behind you at chest height. Arms slightly bent, bring hands together in front. Squeeze chest. Light extra chest stimulus without fatiguing for Friday.",
                "equipment": "Resistance band",
            },
        ],
    },
}

PROGRESSION_TIPS = [
    "POST-HERNIA RULE: No deadlifts until cleared. KB swings and barbell rows hit the same muscles safely.",
    "Squat progression: Air squats -> Goblet squats (25lb KB) -> Empty barbell -> Add weight. No rush.",
    "Incline Bench & OHP: Add 5 lbs/session when you hit the top rep range. Then 2.5 lbs when you stall.",
    "When you stall 3 sessions in a row, deload 10% and work back up.",
    "Chest grows from FREQUENCY - that's why we hit it 3-4x/week (barbell, DB, push-ups, bands).",
    "Focus on FULL STRETCH and SQUEEZE - how many reps doesn't matter if the muscle isn't working.",
    "Alternate heavy weeks (6-8 reps, heavy) and volume weeks (12-15 reps, controlled) every 2 weeks.",
    "Steps goal: 5k minimum every day, 10k on non-lifting days. This alone changes body composition.",
    "Film your squats and incline bench to check form.",
]

TRAINING_PRINCIPLES = [
    "Muscle grows from micro-tears repaired by amino acids - you can break a muscle in 2 hard sets.",
    "Heavy week: Warm-up set, then heavy 6-8 reps, followed by a burnout set at 50-75% weight.",
    "Volume week: 15-30 reps with full stretch and slow squeeze. Let lactic acid build up.",
    "If the muscle isn't dead after your sets, you're wasting time. Intensity > volume.",
    "Always consume protein within 1 hour after training.",
    "Rest 3-5 min between heavy compound lifts, 2-3 min between accessories.",
    "At 49, recovery is king. Sleep 7-8 hours. Band/walk days ARE recovery - active beats sitting.",
    "Band work can be done DAILY - face pulls, pull-aparts, lateral raises. Low fatigue, high benefit.",
    "Post-hernia: Avoid heavy Valsalva (holding breath under load). Breathe through every rep. Brace core without bearing down hard.",
    "KB swings are your deadlift replacement - they train the same hip hinge without the heavy spinal/abdominal loading.",
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
        daily_steps=DAILY_STEPS,
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
