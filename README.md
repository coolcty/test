# AI Learning Management System

An efficient AI learning management system based on MVA (Mathématiques, Vision, Apprentissage) Master's course structure.

## 🎯 System Overview

This system helps you:
- **Master AI comprehensively** with a structured learning plan
- **Automatically schedule daily tasks** based on your progress
- **Track completion status** for each topic
- **Dynamically adjust** the learning pace to maintain efficiency

## 📚 MVA Course Learning Roadmap

### Phase 1: Mathematical Foundations (Weeks 1-4)

| Course | Topics | Duration |
|--------|--------|----------|
| Optimization | Convex optimization, Gradient descent, SGD | 2 weeks |
| Probability & Statistics | Probability theory, Statistical inference | 2 weeks |

### Phase 2: Machine Learning Fundamentals (Weeks 5-10)

| Course | Topics | Duration |
|--------|--------|----------|
| Statistical Learning | PAC learning, VC dimension, Regularization | 3 weeks |
| Kernel Methods | SVM, RKHS, Kernel tricks | 2 weeks |
| Graphical Models | Bayesian networks, Markov random fields | 1 week |

### Phase 3: Deep Learning (Weeks 11-16)

| Course | Topics | Duration |
|--------|--------|----------|
| Neural Networks | MLP, CNN, RNN, Attention | 3 weeks |
| Generative Models | VAE, GAN, Diffusion models | 2 weeks |
| Reinforcement Learning | MDP, Q-learning, Policy gradient | 1 week |

### Phase 4: Advanced Topics (Weeks 17-20)

| Course | Topics | Duration |
|--------|--------|----------|
| Computer Vision | Object detection, Segmentation | 2 weeks |
| Natural Language Processing | Transformers, BERT, GPT | 2 weeks |

## 🗂️ File Structure

```
.
├── README.md           # This file - Learning roadmap
├── schedule.json       # Daily task scheduling system
├── progress.json       # Progress tracking data
└── adjuster.py         # Dynamic adjustment mechanism
```

## 🚀 Getting Started

1. Review your progress in `progress.json`
2. Check today's tasks in `schedule.json`
3. Run `python adjuster.py` to get recommended adjustments
4. Update your progress after completing tasks

## 📊 Usage

### Check Today's Tasks
```bash
python adjuster.py --today
```

### Update Progress
```bash
python adjuster.py --complete "task_id"
```

### Get Recommendations
```bash
python adjuster.py --recommend
```

## 🔄 Dynamic Adjustment Logic

The system adjusts your learning plan based on:
1. **Completion rate** - If below 70%, reduce daily task load
2. **Time spent** - Optimize based on actual vs estimated time
3. **Difficulty feedback** - Adjust topic depth accordingly
4. **Streak tracking** - Maintain momentum with streak bonuses

## 📈 Progress Metrics

- Daily completion rate
- Weekly progress percentage
- Topic mastery level (1-5 stars)
- Learning velocity (topics/week)

---

*This learning system is designed for efficient mastery of AI based on the MVA Master's curriculum.*
