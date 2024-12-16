# data/scripts/dialogue_processor_manual.py

import gradio as gr
import json
import os

class DialoguePairProcessor:
    def __init__(self, input_file_path):
        self.datasets = []
        self.load_datasets(input_file_path)

    def load_datasets(self, file_path):
        """Load dialogues from jsonl file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                self.datasets.append(json.loads(line))

    def generate_training_data(self, inputs, outputs):
        """Generate and save training data from inputs and outputs"""
        input_items = [item for item in inputs.strip().split('\n') if item.strip()]
        output_items = [item for item in outputs.strip().split('\n') if item.strip()]

        training_data = {
            "input": f"[{', '.join(input_items)}]",
            "output": f"[{', '.join(output_items)}]"
        }
        
        # Write to file
        output_file = 'data/train.jsonl'
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(training_data, ensure_ascii=False) + '\n')
            return ("Data saved successfully!", "", "")
        except Exception as e:
            return (f"Error saving data: {str(e)}", "", "")

    def get_dialogue(self, id):
        """Get dialogue content by id"""
        dialogue = self.datasets[id]['dialogue']
        texts = []
        for d in dialogue:
            texts.append(f"{{\"role\": \"{d['role']}\", \"content\": \"{d['content']}\"}}")
        return texts, len(dialogue)

    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(fill_width=True, theme=gr.themes.Origin()) as demo:
            id_comp = gr.Number(value=0)
            
            with gr.Row():
                with gr.Column(scale=2):
                    textboxes = []
                    input_buttons = []
                    output_buttons = []
                    for i in range(16):
                        with gr.Row():
                            with gr.Column(scale=10):
                                text = gr.Textbox(label=f"{i+1}", lines=1, max_lines=1, visible=False)
                            with gr.Column(scale=1, min_width=100):
                                add_to_input = gr.Button("→Input", variant="primary", size="sm", visible=False)
                                add_to_output = gr.Button("→Output", size="sm", visible=False)
                            textboxes.append(text)
                            input_buttons.append(add_to_input)
                            output_buttons.append(add_to_output)
                            
                with gr.Column(scale=1):
                    inputs = gr.Textbox(label="Inputs", lines=5)
                    outputs = gr.Textbox(label="Outputs", lines=5)
                    clear_btn = gr.Button("Clear")
                    generate_btn = gr.Button("Generate Training Data")

            # Set click events
            for i in range(16):
                text = textboxes[i]
                input_btn = input_buttons[i]
                output_btn = output_buttons[i]
                
                input_btn.click(
                    lambda t, cur: cur + t + "\n" if t else cur,
                    inputs=[text, inputs],
                    outputs=inputs
                )
                output_btn.click(
                    lambda t, cur: cur + t + "\n" if t else cur,
                    inputs=[text, outputs],
                    outputs=outputs
                )

            with gr.Row():
                prev_btn = gr.Button('Prev')
                next_btn = gr.Button('Next')

            def on_prev_click(curr_id):
                new_id = max(0, int(curr_id) - 1)
                texts, length = self.get_dialogue(new_id)
                visible_update = [gr.update(visible=False) for _ in range(16)]
                for i in range(length):
                    visible_update[i] = gr.update(visible=True)
                text_values = texts + [""] * (16 - length)
                return [new_id] + \
                       [visible_update[i] for i in range(16)] + \
                       [visible_update[i] for i in range(16)] + \
                       [visible_update[i] for i in range(16)] + \
                       text_values

            def on_next_click(curr_id):
                new_id = min(len(self.datasets) - 1, int(curr_id) + 1)
                texts, length = self.get_dialogue(new_id)
                visible_update = [gr.update(visible=False) for _ in range(16)]
                for i in range(length):
                    visible_update[i] = gr.update(visible=True)
                text_values = texts + [""] * (16 - length)
                return [new_id] + \
                       [visible_update[i] for i in range(16)] + \
                       [visible_update[i] for i in range(16)] + \
                       [visible_update[i] for i in range(16)] + \
                       text_values

            def clear_textboxes():
                return ["", ""]

            prev_btn.click(
                fn=on_prev_click,
                inputs=[id_comp],
                outputs=[id_comp] + textboxes + input_buttons + output_buttons + textboxes
            )
            next_btn.click(
                fn=on_next_click,
                inputs=[id_comp],
                outputs=[id_comp] + textboxes + input_buttons + output_buttons + textboxes
            )

            clear_btn.click(
                fn=clear_textboxes,
                outputs=[inputs, outputs]
            )
            generate_btn.click(
                fn=self.generate_training_data,
                inputs=[inputs, outputs],
                outputs=[outputs, inputs, outputs]
            )

        return demo

def main():
    processor = DialoguePairProcessor(os.path.join(os.path.dirname(__file__), '../partitions/train_dialogues.jsonl'))
    demo = processor.create_interface()
    demo.launch()

if __name__ == "__main__":
    main()