from django import forms

from .models import Post, Comment, BadWords


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        filtered = FilterBadWords()
        return filtered.start_filtering(data)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'group', 'image')

    def clean_title(self):
        data = self.cleaned_data['title']
        filtered = FilterBadWords()
        return filtered.start_filtering(data)

    def clean_subject(self):
        data = self.cleaned_data['text']
        return data

    def clean_text(self):
        data = self.cleaned_data['text']
        filtered = FilterBadWords()
        return filtered.start_filtering(data)


class FilterBadWords:
    """
    Фильтрация 'плохих' слов на основе словаря замен схожих
    символов и расстояния Левенштейна
    """
    bad_words = [*[one.word for one in BadWords.objects.all()]]

    mydict = {
        'а': ['а', 'a', '@'],
        'б': ['б', '6', 'b'],
        'в': ['в', 'b', 'v'],
        'г': ['г', 'r', 'g'],
        'д': ['д', 'd', 'g'],
        'е': ['е', 'e', 'ye'],
        'ё': ['ё', 'e', 'yo'],
        'ж': ['ж', 'zh', '*'],
        'з': ['з', '3', 'z'],
        'и': ['и', 'u', 'i'],
        'й': ['й', 'u', 'i'],
        'к': ['к', 'k', 'i{', '|{', '|['],
        'л': ['л', 'l', 'ji'],
        'м': ['м', 'm'],
        'н': ['н', 'h', 'n'],
        'о': ['о', 'o', '0'],
        'п': ['п', 'n', 'p'],
        'р': ['р', 'r', 'p'],
        'с': ['с', 'c', 's'],
        'т': ['т', 'm', 't'],
        'у': ['у', 'y', 'u'],
        'ф': ['ф', 'f'],
        'х': ['х', 'x', 'h', '}{', ']['],
        'ц': ['ц', 'c', 'u,', 'ts'],
        'ч': ['ч', 'ch'],
        'ш': ['ш', 'sh'],
        'щ': ['щ', 'sch'],
        'ь': ['ь', 'b'],
        'ы': ['ы', 'bi'],
        'ъ': ['ъ'],
        'э': ['э', 'e'],
        'ю': ['ю', 'io', 'yu'],
        'я': ['я', 'ya']
    }

    def __init__(self):
        self.raw_phrase = None

    def censor(self, phrase):
        """Сравнивает запрещенные слова с подготовленными фрагментами фразы."""
        error_set = set()
        for bad_word in self.bad_words:
            for part in range(len(phrase)):
                fragment = phrase[part: part + len(bad_word)]
                if self.levenshtein_distance(fragment, bad_word) <= len(bad_word) * 0.25:
                    error_set.add(bad_word)

        if len(error_set):
            error_list = sorted(list(set(error_set)))
            raise forms.ValidationError(
                f'В заголовке или тексте вы использовали '
                f'запрещенные у нас на сайте слова: {", ".join(error_list)}.'
            )
        else:
            return self.raw_phrase

    @staticmethod
    def comparison(input_dict, input_phrase):
        """Сравнивает символы во фразе с символами в словаре."""
        for key, value in input_dict.items():
            for letter in value:
                for symbol in input_phrase:
                    if letter == symbol:
                        input_phrase = input_phrase.replace(symbol, key)
        return input_phrase

    @staticmethod
    def levenshtein_distance(word_fragment, word):
        """Вычисляет расстояние Левенштейна между фрагментом и словом."""
        n, m = len(word_fragment), len(word)
        if n > m:
            # Make sure n <= m, to use O(min(n, m)) space
            word_fragment, word = word, word_fragment
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if word_fragment[j - 1] != word[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

    def start_filtering(self, input_phrase):
        self.raw_phrase = input_phrase
        input_phrase = input_phrase.lower().replace(' ', '')
        filtered_phrase = self.comparison(self.mydict, input_phrase)
        return self.censor(filtered_phrase)
