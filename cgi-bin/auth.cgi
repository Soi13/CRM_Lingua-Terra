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

my $err="";
my $login=param('firstname');
my $passw=param('passw');

$login=~s/\0//g; $login=~s/\.\.//g; $login=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$passw=~s/\0//g; $passw=~s/\.\.//g; $passw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

if (defined($login) && defined($passw))
{
$passw=md5_hex($passw);

#Проверка на существование пользователя в БД по введенному паролю и логину
#my $dbh=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016") or die "Error: $DBI::errstr\n";
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select * from usr where LOGIN like ? and PASSW like ?";
$sth=$dbh->prepare($sql);
$sth->execute($login,$passw);

#Получаем кол-во строк, если строка одна, то логин и пароль введены верно
my $rows_affected = $sth->rows();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

$dbh->disconnect;

#Если пароль и логин верные, то проверяем статус пользователя и выводим главную форму
if ($row[1] eq $login && $row[2] eq $passw) { 
#if ($rows_affected==1) {

if ($row[48]!=1) #Проверям юзера на блокировку учетки
{
   print "Content-type: text/html\n\n";
   print <<HTML4;
   <!doctype html>
   <html>
   <head>
   <meta charset="windows-1251">
   <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
   <title>CRM - Лингва-Терра</title>
   <link href="../CSS/auth_page.css" rel="stylesheet">
   <script type="text/javascript" src="../JS/auth_check.js"></script>
   <script type="text/javascript" src="../JS/jquery.min.js"></script>
   </head>
   <body>
   <form method="post" class="form-container" action="auth.cgi" onSubmit="return check()" name="forma" id="forma">
   <div class="form-title"><h2>Авторизация</h2></div>
   <div class="form-title">Логин</div>
   <input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
   <div class="form-title">Пароль</div>
   <input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
   <div class="submit-container">
   <input name="btn" id="btn" class="submit-button" type="submit" value="Войти" />
   </div>
   </form>
   <p></p>
   <span class="err">Пользователь $row[1] заблокирован!</span>
   </body>
   </html>
HTML4
exit;
}
else
{
   #Расчет кол-ва дней оставщихся до наступление периода необходимости смены пароля
   my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
   my $sth2=$dbh2->do("SET NAMES 'cp1251'");
   my $sql2="SELECT DATEDIFF(PASSW_DATE_EXPIRED, NOW()) as DAYS from usr where ID=?";
   $sth2=$dbh2->prepare($sql2);
   $sth2->execute($row[0]);
   #В массив записываем извлеченную строку
   my @days = $sth2->fetchrow_array;
   $dbh2->disconnect;
   
   if ($days[0]==0) #Если кол-во дней до изменения пароля 0, то блокируем учетку
   {
      my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
      my $sth3=$dbh3->do("SET NAMES 'cp1251'");
      my $sql3="update usr set ACTIVE=0 where ID=?";
      $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
      $sth3->execute($row[0]);
      $dbh3->disconnect;
      
      print "Content-type: text/html\n\n";
      print <<HTML4;
      <!doctype html>
      <html>
      <head>
      <meta charset="windows-1251">
      <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
      <title>CRM - Лингва-Терра</title>
      <link href="../CSS/blocked_page.css" rel="stylesheet">
      <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
      <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
      <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
      <script type="text/javascript" src="../JS/auth_check.js"></script>
      <script type="text/javascript" src="../JS/jquery.min.js"></script>    
      <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script> 
      </head>
      <body>
      <form method="post" class="form-container" action="" onSubmit="" name="forma" id="forma">
      <p>Ваша учетная запись заблокирована в связи с истечением срока действия пароля. Для разблокировки и возобновления доступа обратитесь к администратору.</p>
      <div class="submit-container">
      <a href="#" class="easyui-linkbutton" onclick="javascript: window.location.replace('http://localhost:6080');">Закрыть</a>
      </div>
      </form>     
      </body>
      </html>      
HTML4

      exit();
   }
   
   #При логине записываем данные залогинивщегося пользовтеля в БД для статистики 
   #my $dbh1=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016") or die "Error: $DBI::errstr\n";
   my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
   my $sth1=$dbh1->do("SET NAMES 'cp1251'");
   my $sql1="insert into logged_users (USER_NAME, REMOTE_ADDR, REMOTE_PORT, REMOTE_HOST, USER_AGENT, DT_TM) values (?,?,?,?,?,NOW())";  
   $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
   $sth1->execute($login, $ENV{'REMOTE_ADDR'}, $ENV{'REMOTE_PORT'}, $ENV{'REMOTE_HOST'}, $ENV{'HTTP_USER_AGENT'});   
   $dbh1->disconnect;
   
   #Подгружаем название организации для вывода ее на странице
    open FF, "<txt_data/name_org.txt";
    my @name_org=<FF>;
    close (FF) or die $!;
   #########################################
   

   
   my $sess=CGI::Session->new("driver:mysql", undef, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die  CGI::Session->errstr();      
   $sess->name('SID');
   my $cookies=cookie(-name=>$sess->name(), -valur=>$sess->id(), -path=>'/', -domain=>'http://localhost:6080');
   print "Set-Cookie: $cookies\n";
   $sess->param(-name=>'Login', -value=>$login);
   $sess->param(-name=>'Password', -value=>$passw);
   $sess->param(-name=>'Status', -value=>$row[4]);  
   $sess->param(-name=>'USER_ID', -value=>$row[0]); 
   $sess->param(-name=>'able_del_dog_stud', -value=>$row[49]);
   $sess->param(-name=>'able_del_zayavki', -value=>$row[50]);
   $sess->param(-name=>'able_del_group', -value=>$row[53]); 
   $sess->param(-name=>'able_del_student_from_group', -value=>$row[54]);   
   $sess->param(-name=>'able_del_lessons_from_group', -value=>$row[55]);
   $sess->param(-name=>'able_set_begin_study', -value=>$row[56]);
   $sess->param(-name=>'able_change_summ_4_opl', -value=>$row[57]);
   $sess->param(-name=>'able_del_period_of_pays', -value=>$row[59]);
   $sess->param(-name=>'days_expired_passw', -value=>$days[0]);
   $sess->param(-name=>'able_send_sms', -value=>$row[65]);
   $sess->param(-name=>'able_add_period_of_pays', -value=>$row[67]);
   $sess->param(-name=>'able_add_event', -value=>$row[69]);
   $sess->param(-name=>'able_edit_event', -value=>$row[70]);
   $sess->param(-name=>'able_del_event', -value=>$row[71]);
   $sess->param(-name=>'able_move_students_between_groups', -value=>$row[72]);
   $sess->param(-name=>'GROUPS_SEKRETARIAT', -value=>$row[7]);
   $sess->param(-name=>'STUDENTS_SEKRETARIAT', -value=>$row[8]);
   $sess->param(-name=>'TEACHERS_SEKRETARIAT', -value=>$row[9]);
   $sess->param(-name=>'ROOMS_SEKRETARIAT', -value=>$row[10]);
   $sess->param(-name=>'CALENDAR_SEKRETARIAT', -value=>$row[11]);
   $sess->param(-name=>'SMS_SEKRETARIAT', -value=>$row[14]);
   $sess->param(-name=>'DOCUMENTS_SEKRETARIAT', -value=>$row[15]);
   $sess->param(-name=>'ZAYAV_SEKRETARIAT', -value=>$row[47]);
   $sess->param(-name=>'PERSONAL_CALENDAR_SEKRETARIAT', -value=>$row[52]);
   $sess->param(-name=>'RESERV_SEKRETARIAT', -value=>$row[58]);
   $sess->param(-name=>'PRIH_ORDER_FINANCE', -value=>$row[21]);
   $sess->param(-name=>'IMPORT_FILES_BANK_FINANCE', -value=>$row[22]);
   $sess->param(-name=>'EXPORT_FILES_BANK_FINANCE', -value=>$row[51]);
   $sess->param(-name=>'OPTIONS_SUPERADMIN', -value=>$row[39]);
   $sess->param(-name=>'REPORTS_REPORTS', -value=>$row[41]);
   $sess->param(-name=>'DEBTS_MONTH_REPORTS', -value=>$row[60]);
   $sess->param(-name=>'PLAN_FACT_REPORTS', -value=>$row[61]);
   $sess->param(-name=>'PLAN_FACT_REAL_PAYS_MONTH_REPORTS', -value=>$row[62]);
   $sess->param(-name=>'STUDENTS_TEACHERS_REPORTS', -value=>$row[66]);
   $sess->param(-name=>'STUDENTS_AGE_REPORTS', -value=>$row[68]);
   $sess->param(-name=>'STUDENTS_DOGOVORS', -value=>$row[73]);   
   $sess->expire("+30m");
   $sess->flush();
   print "Location: sekretariat_main.cgi?SID=" . $sess->id() . "\n\n";   

   exit();
}  
}
#иначе, если пароль и логин не верные
else {
   print "Content-type: text/html\n\n";
   print <<HTML2;
   <!doctype html>
   <html>
   <head>
   <meta charset="windows-1251">
   <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
   <title>CRM - Лингва-Терра</title>
   <link href="../CSS/auth_page.css" rel="stylesheet">
   <script type="text/javascript" src="../JS/auth_check.js"></script>
   <script type="text/javascript" src="../JS/jquery.min.js"></script>
   </head>
   <body>
   <form method="post" class="form-container" action="auth.cgi" onSubmit="return check()" name="forma" id="forma">
   <div class="form-title"><h2>Авторизация</h2></div>
   <div class="form-title">Логин</div>
   <input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
   <div class="form-title">Пароль</div>
   <input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
   <div class="submit-container">
   <input name="btn" id="btn" class="submit-button" type="submit" value="Войти" />
   </div>
   </form>
   <p></p>
   <span class="err">Логин или пароль не верные!</span>
   </body>
   </html>
HTML2
  }
exit();
}

####################################################################################################################################
#Загрузка формы аутентификации. Загружатся при первом входе, когда переменные логина и пароля еще не определенны, т.к. не вводились#
####################################################################################################################################
print "Content-type: text/html\n\n";
print <<HTML3;
<!doctype html>
<html>
<head>
<meta charset="windows-1251">
<META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
<title>CRM - Лингва-Терра</title>
<link href="../CSS/auth_page.css" rel="stylesheet">
<script type="text/javascript" src="JS/auth_check.js"></script>
<script type="text/javascript" src="JS/jquery.min.js"></script>
</head>
<body>
<form method="post" class="form-container" action="cgi-bin/auth.cgi" onSubmit="return check()" name="forma" id="forma">
<div class="form-title"><h2>Авторизация</h2></div>
<div class="form-title">Логин</div>
<input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
<div class="form-title">Пароль</div>
<input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
<div class="submit-container">
<input name="btn" id="btn" class="submit-button" type="submit" value="Войти" />
</div>
</form>
<p></p>
<div id="content"></div>
</body>
</html>
HTML3
