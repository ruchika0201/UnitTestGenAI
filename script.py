import openai
import sys
import os
import fnmatch

openai.api_key = "api_key"
openai.api_base = "api_endpoint"

model = "modelName"

FILE_PATTERN = '*.ts'

def extract_between_words(input_string, start_word, end_word):
    start_index = input_string.find(start_word)
    if start_index == -1:
        return None

    end_index = input_string.rfind(end_word)
    if end_index == -1:
        return None

    extracted_text = input_string[start_index + len(start_word):end_index]
    return extracted_text.strip()  # Remove leading and trailing whitespace


def generateFormattedResponse(content):
    content_to_write = ''
    for c in content:
        content_to_write += c["choices"][0]["text"]
    content_to_write = extract_between_words(content_to_write, '```', '```')
    return content_to_write + '\n'



def readContent(source_file_name):
    try:
        with open(source_file_name, 'r') as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        print(f"Source file '{source_file_name}' not found.")



def generateUts(file_content):
    prompt = "Write unit test for this code in angular:\n" + file_content
    # Standard formatting for LLaMa 2
    prompt = f"<s>[INST] <<SYS>>\nBelow is an instruction that describes a task. Write a response that appropriately completes the request.\n<</SYS>>\n\n{prompt} [/INST] "

    # Standard formatting Open LLaMa
    prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{prompt}\n\n### Response:"
    completion = openai.Completion.create(model=model, prompt=prompt, max_tokens=1000, temperature=0, stream=True)
    return completion

def generateFiles(content_to_write, source_file_name, root):
    target_file_name = source_file_name.replace(".ts", ".spec.ts")
    print(target_file_name)
    target_file_path = os.path.join(root, target_file_name)
    try:
        with open(target_file_path, "a") as file:
            if content_to_write is not None:
                file.write(content_to_write)
            else:
                print("No Content")
    except IOError as e:
        print(f"An error occurred: {e}")


def recursiveFolderWalkThrough(source):
    for root, _, filenames in os.walk(source):
        for filename in fnmatch.filter(filenames, FILE_PATTERN):
            file_path = os.path.join(root, filename)
            file_content = readContent(file_path)
            response = generateUts(file_content)
            formatted_response = generateFormattedResponse(response)
            generateFiles(formatted_response, filename, root)



def main(source):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    print(source_path)
    recursiveFolderWalkThrough(source_path)


if __name__ == "__main__":
    print("Welcome")
    args = sys.argv
    if len(args) != 2:
        raise Exception("You must pass a source directory - only.")

    source = args[1:]
    main(source[0])