import os
import jinja2
from typing import List, Dict, Any

from mover.synthesizers.base_synthesizer import BaseSynthesizer
from mover.synthesizers.utils import extract_code_block, get_svg_code


class AnimationSynthesizer(BaseSynthesizer):
    ## System message file path for animation synthesizer
    _sys_msg_filepath = 'sys_msg_animation_synthesizer.md'
    ## HTML template file path for animation synthesizer
    _html_template_filepath = os.path.join(os.path.dirname(__file__), 'assets', 'template.html')

    def __init__(self, model_name: str = "gpt-4.1", provider: str = "openai", num_ctx: int = 128000, params: Dict[str, Any] = {}):
        """
        Initialize the Animation Synthesizer.
        
        Args:
            model_name: Name of the model to use (default: "gpt-4o")
            provider: LLM provider to use (default: "openai")
            num_ctx: Max context length. Only used for the locally-hosted models (default: 128000)
            params: Additional parameters to pass to the LLM client (default: {})
        """
        super().__init__(model_name=model_name, provider=provider, num_ctx=num_ctx, params=params)
        
        ## Load HTML template
        with open(self._html_template_filepath, 'r') as f:
            self.html_template = f.read()
            
            
    def set_html_template(self, html_template_path):
        """
        Set the HTML template for the animation synthesizer.
        
        Args:
            html_template_path: Path to HTML template file
        """
        self._html_template_filepath = html_template_path
        with open(html_template_path, 'r') as f:
            self.html_template = f.read()


    def compose_initial_user_prompt(self, animation_prompt: str, svg_file_path: str) -> Dict[str, str]:
        """Build initial user prompt with SVG and animation description."""
        svg_code = get_svg_code(svg_file_path)
        initial_prompt_template = jinja2.Template("svg code:\n{{ svg_code }}\n\nprompt:\n{{ animation_prompt }}")
        rendered_prompt = initial_prompt_template.render(svg_code=svg_code, animation_prompt=animation_prompt)
        usr_msg = {"role": "user", "content": rendered_prompt}
        return usr_msg


    def generate(self, chat_history: List[Dict[str, str]], svg_file_path: str = None, html_output_file_path: str = None) -> tuple:
        """
        Generate a new message from LLM and extract JavaScript code from it.
        
        Args:
            chat_history: List of chat messages with role and content, but chat_history is not being updated in this function
            svg_file_path: Path to SVG file for HTML generation
            output_dir: Directory to save HTML file (optional)
            
        Returns:
            tuple: (response, error_msg)
        """
        ## get next message from LLM
        response = self.llm_client.create(chat_history)
        
        ## extract JavaScript code
        try:
            javascript_code = extract_code_block(response, '```javascript', '```')
        except Exception as e:
            error_msg = f"Error extracting code block: {e}"
            return response, error_msg
        
        ## write javascript code to html if output_dir is specified
        if html_output_file_path is not None and svg_file_path is not None:
            svg_code = get_svg_code(svg_file_path)
            html_code = self.html_template.replace("{{svg-code}}", svg_code)
            html_code = html_code.replace("let placeholder = 0;", javascript_code)
            
            ## raise error if directory of html_output_file_path is not a valid directory
            if not os.path.isdir(os.path.dirname(html_output_file_path)):
                raise ValueError(f"Invalid directory: {os.path.dirname(html_output_file_path)}")
            
            with open(html_output_file_path, "w") as f:
                f.write(html_code)
        
        return response, None