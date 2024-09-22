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
my $able_set_begin=$sess->param('able_set_begin_study');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

   if ($able_set_begin==1) #Смотрим имеет ли возможноть пользователь удалять группы. Определям это по парамметру переданному из сессии.
   {
        my $id=param('id_st');
        my $date=param('DATE_ST_BEG');
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $date=~s/\0//g; $date=~s/\.\.//g; $date=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        ########Проверка на ввод даты начала обучения
        if (length($date)==0)
        {
           my $ans="Необходимо заполнить \"Дата начала обучения\"!";
           #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;  
        }
        ##############################################################
        
        #Проверка корректности даты
        ## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
        if ($date!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
           my $ans="Введенная дата начала не корректна. Формат должен быть, например, 2016-05-30.";
           #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;
        }
        
        ###########################################################################################################################################
        # Разбираем дату на день месяц и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
        ###########################################################################################################################################
        
        # Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
        $date=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
           my $ans="В введенной дате не корректен месяц. Месяц не может быть больше 12!";
           #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;
        }
        
        # Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
        $date=~/\d{4}/;
        if ($&>3000)
        {
           my $ans="В введенной дате не разумно большой год.";
           #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;
        }
        
        # Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
        $date=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
           my $ans="В введенной дате не корректно задано число! Число не может быть более 31!";
           #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;
        }
        ############################################################################################################################################        
        
                
        #вставляем дату начала обучения
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update groups_students set BEGIN_STUDY=? where ID=?";
        $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
        $sth2->execute($date, $id);             
        $dbh2->disconnect;
   
        my $ans="Дата установлена успешно!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        ############################################################
   }
   else
   {
        my $ans="Вы не имеете права устанавливать время начала обчучения у студентов!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
   }
   
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
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
