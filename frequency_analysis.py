from collections import Counter 
import json 


def main() -> None: 
    with open(TEXT, "r", encoding="utf-8") as file: 
        text = file.read() 
        frequency = Counter( char for char in text if char in symbols ) 
        print("Буква - Количество") 
        for symbol in symbols: 
            print(f"{symbol} - {frequency[symbol]}") 
        with open("frequency.json", "w", encoding="utf-8") as file: 
            json.dump( dict(frequency), file, ensure_ascii=False, indent=4 )


TEXT = "warandpeace.txt"

symbols = "аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОпПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ .,!?-:;\"'()1234567890"

if __name__ == "__main__":
    main()