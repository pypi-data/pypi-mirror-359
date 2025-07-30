import os
from typing import List, Dict
from mover.synthesizers.base_synthesizer import BaseSynthesizer
from mover.synthesizers.utils import extract_code_block

class MoverSynthesizer(BaseSynthesizer):
    ## System message file path for mover synthesizer
    _sys_msg_filepath = 'sys_msg_mover_synthesizer.md'

    def compose_initial_user_prompt(self, prompt: str) -> Dict[str, str]:
        """Build initial user prompt."""
        usr_msg = {"role": "user", "content": prompt}
        return usr_msg
    
    
    def get_dsl_documentation(self) -> str:
        """Get DSL documentation."""
        ## check if the system message contains the API documentation
        header = "### Verification DSL Documentation"
        if header not in self.read_sys_msg():
            raise ValueError(f"System message does not contain the proper header {header}.")
        
        return self.read_sys_msg().split(header)[1].lstrip('\n')


    def generate(self, chat_history: List[Dict[str, str]], program_file_path: str = None) -> str:
        """
        Generate a new message from LLM.
        
        Args:
            chat_history: List of chat messages with role and content, but chat_history is not being updated in this function
            program_file_path: Path to save the generated program
            
        Returns:
            str: The generated response from the LLM
        """
        ## get next message from LLM
        response = self.llm_client.create(chat_history)
        
        ## extract JavaScript code
        error_msg = None
        try:
            mover_code = extract_code_block(response, '```', '```')
        except Exception as e:
            error_msg = f"Error extracting code block: {e}"
            
        ## write program to file if program_file_path is specified
        if program_file_path is not None:
            ## raise error if directory of program_file_path is not a valid directory
            if not os.path.isdir(os.path.dirname(program_file_path)):
                raise ValueError(f"Invalid directory: {os.path.dirname(program_file_path)}")
            
            with open(program_file_path, 'w') as f:
                f.write(mover_code)
            
        return response, error_msg
