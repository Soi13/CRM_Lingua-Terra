#!/usr/bin/perl -w
use strict;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI qw(:cgi);
       
print "Content-type: text/html\n\n";
print <<HTML;
<!DOCTYPE html>
<html>
    <head>
    	<meta charset="windows-1251>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">		
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
		<META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW">
        <title>Руководство по использованию системы</title>
		 <link rel="stylesheet" href="../css/normalize.css">
        <link rel="stylesheet" href="../css/demo.css">
		<link rel="stylesheet" href="../css/pushy.css">   
        <script src="../js/jquery.min.js"></script>			
		
    </head>
    <body>

        <header class="site-header push">Руководство по использованию системы</header>
        
HTML

#Подгружаем меню для вывода ее на странице
open FF, "<txt_data/menu.txt";
my @menu=<FF>;
foreach my $str (@menu)
{
  $str=~s/\0//g;
  $str=~s/\.\.//g;  
}
close (FF) or die $!;
print @menu;
#########################################

print <<HTML1;
        <!-- Site Overlay -->
        <div class="site-overlay"></div>

        <!-- Your Content -->
        <div id="container">
            <!-- Menu Button -->
            <button class="menu-btn">&#9776; Меню</button>
			
            <p>В главном разделе одображается сводная и статистическая информация о текущем состоянии дел школы. Данный раздел является информационным.</p>
            <p><img src="../img/sekretariat_main.jpg" width="917" height="397" alt="Секретариат_главная"></p>
            <p>Здесь представлена статистика обучающихся по филиалам, статистика по пололвому признаку, список ДР на текую дату, также присутствует информация по кол-ву принятых заявок и зарегистрированных студентах.</p>
			

        </div>

        <footer class="site-footer push">&copy;<strong> 2016</strong>&nbsp;|&nbsp;<strong>Центр иностранных языков &quot;Лингва-терра&quot;</strong></footer>

        <!-- Pushy JS -->
        <script src="../js/pushy.min.js"></script>

    </body>
</html>
       
HTML1

