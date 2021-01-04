# Meaning-Parser

This parser can predict meaning of any article. For that you need to parse any resources with articles by using our pikabu or yandex dzen parsers or write your own. 

articles must be stored as: 

{
  "_id": "Uniqle ID",
  "content": "ARTICLE CONTENT" 
}

after you need to determ default set of meaning from parsed articles in last step 
default meaning set you can see in meanings.json

you determ meaning and select articles which math to this meaning (!IMPORTANT select articles from parsed in last step)

after you need start article parser createdefault set function to create first base data set

Now this ArticleParser can predict Any article meaning 

to improve prediction you can start selfTeaching function, which take articles and automaticle update TF-IDF data set 

