<!DOCTYPE html>
<html lang="ru">
 <head>
  <meta charset="utf-8"/>
  <link rel="stylesheet" href="/css/reset.css" />
  <link rel="stylesheet" href="/css/main.css"/>
  <script src="/js/jquery-1.7.2.min.js"></script>
  <script>var lang = "${lang}";</script>
  <script src="/js/jed.js"></script>
  <script src="/js/locale/${lang}/messages.js"></script>
  <script src="/js/udf.js"></script>
  <script src="/js/common.js"></script>
  <%block name="Links"></%block>
  <title><%block name="Title"></%block></title>
  <%block name="Style"></%block>
<!-- Google Analytics -->
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-54422334-1', 'auto');
  ga('send', 'pageview');

</script>
<!-- End Google Analytics -->
 </head>

 <body>
  <div id="center">
   <%include file="header.mako"/>
   <div id="body">
    <div id="main">
     <%include file="top_nav.mako"/>
     <div id="content"><%block name="Content"/></div>
    </div>
    <%include file="footer.mako"/>
   </div>
  </div>
 </body>
</html>
