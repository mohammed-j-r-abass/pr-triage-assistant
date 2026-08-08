def final_c_prompt(consensus_model_prompt, model_one, model_two, model_three):
   c_prompt = f"""
               [SYSTEM INSTRUCTION]
               {consensus_model_prompt}

               [MODEL ONE OUTPUT]
               {model_one}

               [MODEL TWO OUTPUT]
               {model_two}

               [MODEL THREE OUTPUT]
               {model_three}
               """
   return c_prompt