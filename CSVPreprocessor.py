def processCSV(input_file, output_file):

    def replace_middle_double_quote(line):
        """Replaces the middle occurrence of a double quote in the line."""
        quote_indices = [i for i, char in enumerate(line) if char == '"']
        if len(quote_indices) % 2 != 0:  # Unmatched quotes exists
            middle_index = quote_indices[len(quote_indices) // 2]
            # Replace the middle quote with a single quote
            line = line[:middle_index] + "'" + line[middle_index + 1:]
        return line

    # Open relevant files
    with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8') as outfile:
        
        for line in enumerate(infile, start=1):
            original_line = line.strip()
            fixed_line = replace_middle_double_quote(original_line)
            
            if original_line != fixed_line:
                print(f"Fixed unmatched quote")
                print(f"New line: {fixed_line}")
            
            outfile.write(fixed_line + '\n')
    
    print(f"CSV preprocessed")
