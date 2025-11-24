# Example Wellness Check-in Conversations

This document shows example conversations demonstrating the wellness companion's flow.

---

## Example 1: First Check-in (No Prior Data)

**Agent:** Hi! Welcome. I'm your wellness companion. How are you feeling today?

**User:** I'm feeling a bit stressed, to be honest.

**Agent:** I hear you. What's your energy like right now?

**User:** Pretty low. I didn't sleep well.

**Agent:** That's tough. What are 1–3 things you'd like to get done today?

**User:** I need to finish a project report and maybe get some exercise if I have energy.

**Agent:** Those sound like good goals. Maybe start with the easiest task first, and even a 10-minute walk could help boost your energy a bit.

**Agent:** So today you're feeling stressed, your energy is low, and your main goals are finishing the project report and getting some exercise. Does that sound right?

**User:** Yes, that's right.

**Agent:** *(saves check-in using tool)*

**Agent:** Perfect! I've saved your check-in. Remember: finish project report, get some exercise. You've got this! One step at a time.

---

## Example 2: Second Check-in (With Memory)

**Agent:** Hey! Welcome back. Last time you mentioned you wanted to finish a project report and get some exercise. How did that go?

**User:** I finished the report! But I didn't manage to exercise.

**Agent:** That's great you got the report done! How are you feeling today?

**User:** Much better now. More relieved.

**Agent:** Wonderful! What's your energy like today?

**User:** Medium, I'd say. Better than yesterday.

**Agent:** That's progress! Any goals for today?

**User:** Yeah, I want to go for that walk I missed yesterday, and also catch up on some reading.

**Agent:** Nice! A 5–10 minute walk could really help, and it's great you're making time for yourself with reading.

**Agent:** So today you're feeling relieved, your energy is medium, and your goals are going for a walk and catching up on reading. Sound good?

**User:** Perfect!

**Agent:** *(saves check-in using tool)*

**Agent:** Perfect! I've saved your check-in. Remember: go for a walk, catch up on reading. Remember to be kind to yourself today. You're doing great! 💪

---

## Example 3: Addressing Stress

**Agent:** Hi! How are you doing emotionally today?

**User:** Honestly, I'm feeling really overwhelmed. I have so much to do.

**Agent:** I'm sorry you're feeling that way. What's your energy like?

**User:** High anxiety energy, if that makes sense.

**Agent:** It absolutely does. Is there anything you want to do just for yourself today? Maybe rest, a walk, or a hobby?

**User:** I should probably take a break, but I feel like I can't afford to. I need to study for exams, clean the house, and call my parents.

**Agent:** Those are all important, but breaking that big list into smaller steps might feel less overwhelming. Maybe pick just one or two for today?

**Agent:** So you're feeling overwhelmed with high anxiety energy, and you're thinking about studying for exams and maybe one other thing. Does that sound manageable?

**User:** Yeah, let's say studying and calling my parents.

**Agent:** *(saves check-in using tool)*

**Agent:** Perfect! I've saved your check-in. Remember: study for exams, call your parents. Sounds like you could use a break - even 5 minutes helps. Be kind to yourself. 💙

---

## Key Flow Elements Demonstrated

✅ **Memory Reference**: Example 2 shows natural reference to past goals  
✅ **Empathetic Listening**: Acknowledging feelings without judgment  
✅ **Practical Advice**: Simple, non-medical suggestions  
✅ **Confirmation**: Always recap and get user confirmation  
✅ **Encouragement**: Ending on a positive, supportive note  
✅ **One Question at a Time**: Never overwhelming the user  
✅ **Flexibility**: Adapting advice to the user's specific situation  

---

## What the Agent Avoids

❌ Medical diagnosis ("You might be depressed")  
❌ Clinical terms ("That sounds like burnout syndrome")  
❌ Prescriptive commands ("You must exercise daily")  
❌ Judgmental responses ("You should have done better")  
❌ Long-winded responses (keeps it to 1-2 sentences)  
❌ Multiple questions at once  

---

## Data Saved to wellness_log.json

### Example 1:
```json
{
  "date": "2025-11-24",
  "time": "09:15:30",
  "mood": "stressed",
  "energy_level": "low",
  "goals": ["finish project report", "get some exercise"],
  "notes": "didn't sleep well",
  "timestamp": "2025-11-24T09:15:30+05:30"
}
```

### Example 2:
```json
{
  "date": "2025-11-24",
  "time": "14:22:15",
  "mood": "relieved",
  "energy_level": "medium",
  "goals": ["go for a walk", "catch up on reading"],
  "notes": "finished the project report from yesterday",
  "timestamp": "2025-11-24T14:22:15+05:30"
}
```

### Example 3:
```json
{
  "date": "2025-11-24",
  "time": "19:45:00",
  "mood": "overwhelmed",
  "energy_level": "high anxiety energy",
  "goals": ["study for exams", "call my parents"],
  "notes": "feeling pressure from multiple responsibilities",
  "timestamp": "2025-11-24T19:45:00+05:30"
}
```
