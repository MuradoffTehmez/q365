import re

# requirements.txt faylının yolunu düzəldin
input_path = r"C:\Q365\q360\requirements.txt"
output_path = r"C:\Q365\q360\cleaned_requirements.txt"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []
for line in lines:
    # Versiya hissəsini təmizləyir, məsələn: 'package==1.2.3' -> 'package'
    cleaned_line = re.sub(r"(==|>=|<=|>|<|~=).*$", "", line).strip()
    if cleaned_line:  # boş sətrləri əlavə etmə
        cleaned_lines.append(cleaned_line + "\n")

with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"Təmizlənmiş requirements faylı '{output_path}' ünvanında yaradıldı.")
