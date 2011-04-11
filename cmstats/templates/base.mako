<%def name="onload()"></%def>
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>CMStats</title>
        <link rel="stylesheet" type="text/css" href="/static/css/core.css" />
        
        <script type="text/javascript" src="http://www.google.com/jsapi"></script>
        <script type="text/javascript">
        google.load("jquery", "1.5.2");
        google.load("jqueryui", "1.8.11");
        
        google.setOnLoadCallback(function() {
            jQuery(function($){
                ${self.onload()}
            });
        });
        </script>
    </head>
    <body>
    ${next.body()}
    </body>
</html>