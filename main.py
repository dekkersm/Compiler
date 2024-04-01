from cpl_lexer import CPLLexer


if __name__ == '__main__':
    data = '''
a, b: float;
{
input(a);
input(b);
    if (a < b)
       output(a);
    else
       output(b);
{
{{{{{{}}}}}}
    5123 3427.7901
    switch (hello) {
        case: myname; break;
        /*case : checkMe;
        if (input == != || && ALL) {*/
            input output; ;;;; 
        } else while do default:::;(){}intfloat in t float int floa while t,:;= == ===
        a + - =- _+-+
        >= = => >= >>=> <<=< <=< =>> => <= == != ! = !! & &&& &&
        static_cast<int> static_cast<float> static__cast static_cast< float> STATIC_CAST<int>
    }
Hello, World!
&& ||| {()}
'''
    lexer = CPLLexer()
    for tok in lexer.tokenize(data):
        print(tok)
