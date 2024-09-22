#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Time::Local;
use Date::Calc qw(:all);
use LWP::UserAgent; 

my $cgi = CGI->new;
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
        print "Location: http://localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $us_id=$sess->param('USER_ID');
my $able_send_sms=$sess->param('able_send_sms');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
        
if ($able_send_sms==1) #Смотрим имеет ли возможноть пользователь отправлять СМС. Определям это по парамметру переданному из сессии.
{ 
   
   #Получаем логин и пароль от СМС шлюза и БД
   my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
   my $sth4=$dbh4->do("SET NAMES 'cp1251'");
   my $sql4="select LOGIN, PASSW from sms_gate";
   $sth4=$dbh4->prepare($sql4);
   $sth4->execute();
   #В массив записываем извлеченную строку
   my @row_data = $sth4->fetchrow_array;
   
   if (!@row_data)
   {
      my $ans="Не укзаны настройки СМС - шлюза. Сделать это можно в разделе \"СМС-шлюз\" меню <a href=\"administration_tools.cgi?SID=$SID\">\"Суперадмин-Настройки\"</a>";
      #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      exit;
   }
   
   my @data=param('data');
  
   if (scalar(@data)==0)
   {
      my $ans="Не выбраны студенты для отправки СМС!";
      #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      exit;
   }  
   
    foreach my $m (@data)
   {
        $m=~s/\0//g;
        $m=~s/\.\.//g;
        $m=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;       
   }

   for (my $g=0; $g<=$#data; $g=$g+3)
   {
        $data[$g]=~s/\D//gs; #Убираем из номера телефона любые символы кроме цифр.                
        
        #Проверка на длинну номера
        if (length($data[$g])!=11)
        {
            next;
        }
        ###########
        
        #Проверка на первую цифру 7 в номере телефона
        if (substr($data[$g],0,1)!=7)
        {
            next;
        }
        ###########
   }



   my $login = $row_data[0];
   my $password = $row_data[1];

   #Создание XML структры для отправки СМС рассылки
   my $first_part = '<?xml version="1.0" encoding="UTF-8"?>    
    <SMS> 
    <operations>  
    <operation>SEND</operation> 
    </operations> 
    <authentification>    
    <username>'.$login.'</username> 
    <password>'.$password.'</password>
    </authentification>   
    <message> 
    <sender>LinguaTerra</sender>    
    <text>Здравствуйте! Оплатите пожалуйста долг %1% руб. по договору №%2%</text>   
    </message>    
    <numbers>'; 
    
   my $second_part = '</numbers>
                      </SMS>';

   my @numbers;
   #Наполняем массив номерами для отправки и суммами долга и тегами <numbers>
   for (my $g1=0; $g1<=$#data; $g1=$g1+3)
   {
      push (@numbers, "<number variables=\"".$data[$g1+1]."; ".$data[$g1+2]."\">".$data[$g1]."</number>");
   }
   #Преобразуем заполненный массив в строку для вставки его в XML структуру
   my $middle_part = join("", @numbers);

   #Строим окончательную XML структуру с номерами для рассылки
   my $ready_XML=$first_part.$middle_part.$second_part;
   

   #Отправляем эту сумму по смс
   my $ua = new LWP::UserAgent;

   my $response = $ua->post('http://api.myatompark.com/members/sms/xml.php',{ XML => $ready_XML});


   my$ans="Рассылка проведена удачно!";
   Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
   my $res=$ans;
   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});
   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   ############################################################  

   #Удаление сессии
   sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

}
else
{
        my $ans="Вы не имеете права отправлять СМС!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
}






}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
