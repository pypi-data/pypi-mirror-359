def shame_insult(smelly, total):
    if total == 0:
        return "🦴 No tests, no pride. This isn't software, it’s improvisational comedy lab."
    
    ratio = smelly / total

    if ratio == 0:
        return "🧼 Did you handcraft these with soap and prayer? Go flex elsewhere."
    elif ratio <= 0.2:
        return "🙄 You passed, but only because the bar is on the floor."
    elif ratio <= 0.5:
        return "🤢 I've seen spaghetti code with more structure than these tests."
    elif ratio <= 0.8:
        return "🚨 Is this a test suite or a stress test for your team?"
    elif ratio < 1.0:
        return "🔥 Your tests are a dumpster fire, and you brought the gasoline."
    else:
        return "🧨 Every test here is a landmine. Stop writing code and start apologizing."