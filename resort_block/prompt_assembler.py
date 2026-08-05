def final_prompt(system_prompts, pr_data):
   prompt = f"""
               [SYSTEM INSTRUCTION]
               {system_prompts}

               [PR DATA]
               {pr_data}

               [INSTRUCTION]
               Based on only the context, generate a response.
            """
   return prompt