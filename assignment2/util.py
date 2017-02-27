def dot_product(vector1,vector2):
    result = 0
    for key,value in vector1.items():
        result = result + value*vector2.get(key,0)
    return result

def bold_query_tokens(snippet,tokens):
    start_tag = '<strong>'
    end_tag = '</strong>'
    for token in tokens:
        snippet = snippet.replace(token,start_tag+token+end_tag)
    return snippet

def get_snippet(text, query):
    #words to be considered before and after the token
    words_before_token = 7
    words_after_token = 13
    supposed_words_in_snippet = words_before_token+words_after_token
    dots = '...'

    query_tokens = query.split()
    text_tokens = text.split()

    found_index = -1
    snippet = ''
    #finding snippet for the first word in title and if not found then searching second and so on
    for i in range(0,len(query_tokens)):
        try:
            found_index = text_tokens.index(query_tokens[i])
            break;
        except ValueError:
            pass
            #continue to search next query token in text
    if found_index != -1:
        start_index = max(0,found_index-words_before_token)
        end_index = min(found_index+words_after_token,len(text_tokens))
        actual_words_in_snippet = end_index-start_index
        diff_in_words = supposed_words_in_snippet-actual_words_in_snippet
        if diff_in_words > 0:
            if (end_index + diff_in_words) < len(text_tokens):
                end_index += diff_in_words
            elif start_index-diff_in_words >= 0 :
                start_index -= diff_in_words
        #adding dots to begining and end of snippet
        if start_index>0:
            text_tokens[start_index] = dots+text_tokens[start_index]
        if end_index<len(text_tokens):
            text_tokens[end_index-1]=text_tokens[end_index-1]+dots
        snippet = " ".join(text_tokens[start_index:end_index])
        snippet = bold_query_tokens(snippet,query_tokens)
    return snippet
