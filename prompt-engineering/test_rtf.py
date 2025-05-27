from utils import read_rtf_file

# Test the read_rtf_file function with a sample RTF file
file_path = "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-2.rtf"
result = read_rtf_file(file_path)

if result:
    if result['date_time']:
        print(f"Date and time extracted: {result['date_time']}")
        print(f"Formatted date: {result['date_time'].strftime('%Y-%m-%d')}")
        print(f"Formatted time: {result['date_time'].strftime('%H:%M')}")
    else:
        print("Date and time could not be extracted.")
    
    print("\nExtracted text:")
    print(result['text'][:200] + "..." if len(result['text']) > 200 else result['text'])
else:
    print("Failed to read the RTF file.")