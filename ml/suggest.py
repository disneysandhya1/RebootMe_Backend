# ml/suggest.py
def recommend_action(mood_score, water_count, stretch_done):
    if mood_score < 2:
        return "Take a short walk or do a calming breath exercise 🌿"
    if water_count < 5:
        return "Hydrate! Drink a glass of water 💧"
    if not stretch_done:
        return "Do a 1-minute neck or back stretch 🙆‍♂️"
    return "You're doing great! Keep it up 💪"
