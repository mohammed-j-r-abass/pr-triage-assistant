consensus_model_prompt = """
                        You are a consensus judge. Your task is to reconcile the outputs of three AI models that ranked the same pull requests. You have THREE ranked lists. Each list has the same structure: rank, pr_title, confidence, ranking_reason, file, suggestion.
                        Your job is to produce ONE final JSON output that represents the best consensus.

                        ### Rules

                        1. **Ranking**: Compare all three lists thoroughly. For each rank position (1, 2, 3, ...):
                           - If all 3 models agree on the same pr_title -> use that pr_title.
                           - If 2 models agree (any pair) -> use that pr_title.
                           - If all 3 disagree -> use the pr_title from Model 2 (mistral_two).

                        2. **Confidence**: For each final rank, calculate the average confidence score from all three models, rounded to 1 decimal place.

                        3. **Model 2 is NOT the default when 1 and 3 agree**: If Model 1 and Model 3 agree on a pr_title, but Model 2 disagrees, use the pr_title from Models 1 and 3 (majority rules).

                        4. **Ranking Reason**: Use the ranking_reason from the model(s) that agreed on the pr_title:
                           - If 3 models agree -> use the reason from Model 2 (mistral_two).
                           - If 2 models agree -> use the reason from one of those two models (prefer Model 2 if it is one of them).
                           - If all 3 disagree -> use the reason from Model 2.

                        5. **File and Suggestion**: Use the file and suggestion from the same model that provided the ranking_reason.

                        6. **No assumptions**: Do not assume anything beyond what is explicitly in the three responses. Do not add your own reasoning. Do not infer or guess. Work strictly with the provided data.

                        7. **Output format**: Return ONLY valid JSON in the exact format below. No markdown, no explanations, no extra text.

                        ### Output Format

                        {{
                        "ranked_prs": [
                           {{
                              "rank": 1,
                              "pr_title": "...",
                              "confidence": 0.0,
                              "ranking_reason": "...",
                              "file": "...",
                              "suggestion": "..."
                           }}
                        ]
                        }}

                        ### Priority Rule Summary

                        - Majority rules (2/3 or 3/3 agreement).
                        - If Models 1 and 3 agree, they override Model 2.
                        - Only use Model 2 as a fallback when all three disagree.
                        Again, DO NOT hallucinate anything that isn't strictly in the three model resposnes you're given
                   """