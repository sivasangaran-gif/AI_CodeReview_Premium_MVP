---
title: AI Code Review Assistant Premium MVP
emoji: 🤖
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 8501
pinned: false
tags: [openenv, pytorch-hackathon, agentic-ai]
---

# AI Code Review Assistant

An autonomous AI agent designed for the **Meta PyTorch Hackathon x Scaler**. 
Built on the **OpenEnv** framework, this assistant reviews pull requests, identifies logical bugs, and provides actionable code quality feedback.

## 🚀 Environment Description
This environment simulates a professional Code Review workflow. It includes multi-file PR support, reward-based evaluation, and deep logic analysis.

- **Action Space**: `read_file`, `add_comment`, `request_changes`, `approve`.
- **Observation Space**: PR details, File content, Line-by-line comments, Execution traces.
- **Difficulty**: Intermediate (Logic-heavy scenarios).

## 📊 Baseline Evaluation Scores
| Metric | Baseline Score (Random) | Baseline Score (LLM Agent) | Target Score |
| :--- | :--- | :--- | :--- |
| **Logic Accuracy** | 0.15 | 0.72 | 0.90+ |
| **Security Detection** | 0.10 | 0.65 | 0.85+ |
| **Response Quality** | 0.20 | 0.80 | 0.95+ |
| **Avg. Reward** | 0.18 | 0.74 | 0.88+ |

## 🛠️ Usage
Visit the main Space URL to view the **Premium UI**. The backend API is exposed on the primary port to support autonomous agent evaluation.

## 📥 Setup
```bash
npx openenv push . --repo-id Siddhaarth07/AI_CodeReview_Premium_MVP
```
Ensure `HF_TOKEN` is set in your Space settings.
