#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use ConnectDB;

my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='path';
        }
else {
        print "Location: http://students.localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://students.localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://students.localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://students.localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');


#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
        #Подгружаем название личный кабинет для вывода ее на странице
        open FF, "<txt_data/pers_room.txt";
        my @pers_room=<FF>;
        foreach my $str (@pers_room)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################
        
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select FIO from pupils where Num_dogovor like ?";
        $sth=$dbh->prepare($sql);
        $sth->execute($num_dog);

        #В массив записываем извлеченную строку
        my @row = $sth->fetchrow_array;

        $dbh->disconnect;

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;
        
        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@pers_room</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxscheduler.css">        
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxchart.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css"> 
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../JS/dhtmlxchart.js"></script>
 

        <script>
        function confirm1(){
        \$.messager.confirm('Внимание', 'Вы уверены, что необходимо выйти', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increase time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("https://students.localhost:6080")}
                                });  });    </script>

        <script> //Отправка формы смены пароля
        function call() {
        var msg   = \$('#ff').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_psw.cgi?SID=$SID',
          data: msg,
          success: function(res) {alert(res.result); \$('#ff')[0].reset(); \$('#w').window('close');},
          error: function() {alert("did not work");}
        });

       }
       </script>
	   
	   <script> //Проверяем долги студента
       \$(function(){	
         \$.ajax({
            type: 'GET',
            url: 'check_debt_student.cgi?SID=$SID',
            cache: false,
            success: function(res) {   
                                       if (res.summ_debt_curr_per!=0)
                                       {
                                        \$('#dlg_window_debt').window('open').dialog('center').dialog('setTitle','Информация о долге');
                                        \$('#debt').text('Ваш текущий долг: '+res.summ_debt_curr_per+' руб.');                                        
                                       }
                                     },
            error: function() {alert("did not work");}
            });
                
        })
        </script>
       
      
        
        </head>
        <body class="easyui-layout" onload="">
        <!--Верхний DIV - заголовок -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@pers_room</h1>
        <!--DIV В котором лежат кнопки панели-->
HTML
        #Подгружаем кнопки, которые лежат на верхней панеле
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #На всяк случай удаляем тэги <script>
           $str_but=~s/SID=\$SID/SID=$SID/i; #Подставляем регуляркой ссам SID в тексте вместо переменной $SID. Сам он не подставляется, т.к. кнопки грузятся из текстового файла.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        #########################################
        
        print <<HTML1;        
        <!--Конец DIV В котором лежат кнопки панели-->
        </div>
        <!--Конец верхний DIV - Заголовок -->

        <!--Левый DIV раздел меню -->
        <div data-options="region:'west',split:false,title:'Меню'" style="width:205px;">
HTML1
        #Подгружаем меню
        open FF2, "<txt_data/main_menu.txt";
        my @menu_panel=<FF2>;
        foreach my $str_menu (@menu_panel)
        {
           $str_menu=~s/\0//g;
           $str_menu=~s/\.\.//g;
           $str_menu=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #На всяк случай удаляем тэги <script>
           $str_menu=~s/SID=\$SID/SID=$SID/i; #Подставляем регуляркой ссам SID в тексте вместо переменной $SID. Сам он не подставляется, т.к. кнопки грузятся из текстового файла.
        }
        close (FF2) or die $!;        
        print @menu_panel;
        #########################################       
        
        print <<HTML2;   
        </div>
        <!--КОнец Левый DIV раздел меню -->

        <!-- Правый DIV раздел подробности -->
        <!--<div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;">-->
        <!--</div>-->
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Главная. Студент: $row[0]'">

           <div style="margin-top: 25px; margin-left:20px;">
                <a href="https://us02web.zoom.us/j/9510088475?pwd=MmNyb0djck9Kb3cwaTRoL0p0WFFxdz09"><span style="font-size:18px;">Подключиться к уроку</span></a>
           </div>

       

        </div>
        <!-- Конец центральный DIV -рабочая область -->

        <!-- Форма изменения пароля -->
        <div id="w" class="easyui-window" title="Смена пароля" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>Текущий пароль:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>Новый пароль:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>Еще раз:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="Подтвердить"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- Конец форма изменения пароля -->
	
	<!-- Форма вывода долга -->    
    <div id="dlg_window_debt" class="easyui-dialog" style="width:400px;height:200px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg_buttons_debt" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">             
            <div style="margin-left:5%; margin-bottom:40px;">
              <span id="debt" style="font-size: 14pt; font-weight: bold; float: left; color: red;"></span>
            </div>     
            
            
    </div> 
    <div id="dlg_buttons_debt">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="javascript:\$('#dlg_window_debt').dialog('close')" style="width:90px">Закрыть</a>
    </div>
    <!-- Конец Форма вывода долга -->
    
    
        </body>
        </html>
HTML2

#Продлеваем время жизни сессии
$sess->atime(time());
$sess->flush();

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://students.localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }

}
else { print "Location: http://students.localhost:6080\n\n"; }