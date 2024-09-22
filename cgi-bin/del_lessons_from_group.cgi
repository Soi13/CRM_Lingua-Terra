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
my $able_del_lessons=$sess->param('able_del_lessons_from_group');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

   if ($able_del_lessons==1) #Смотрим имеет ли возможноть пользователь удалять зантяия в группе. Определям это по парамметру переданному из сессии.
   {
        my $id=param('id_group');
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        #######################Проверяем, есть ли привязанные студенты к данной группе. Если да, то удалять занятия нельзя!###########################
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($id);
        #В массив записываем извлеченную строку
        my @row_gr_id = $sth->fetchrow_array;
                
        if (@row_gr_id)
        {
            my $ans="К группе привязаны студенты, удаление занятий невозможно!";
            #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        #######################################################################################################################################################################
                
        #Если у к группе не привязаны стеднты, то все в порядке, можно удалять занятия
        #Получаем UID группы для удаления расписания и календаря занятий
        my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="select UUID from lessons where GROUP_ID=?";
        $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
        $sth1->execute($id);
        my @row_uuid_les = $sth1->fetchrow_array;
        
        #Удаляем занятия из календаря группы
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="delete from lessons_group where UUID_LESSONS=?";
        $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
        $sth2->execute($row_uuid_les[0]);  
        
        #Удаляем список занятий группы
        my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="delete from lessons_list where UUID_LESSONS=?";
        $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
        $sth3->execute($row_uuid_les[0]);  
        
        #Удаляем саму главную запись занятия из таблицы lessons
        my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth4=$dbh4->do("SET NAMES 'cp1251'");
        my $sql4="delete from lessons where GROUP_ID=?";
        $sth4=$dbh4->prepare($sql4); #Для операций которые не возвращают значение
        $sth4->execute($id);  
        
        $dbh->disconnect;
        $dbh1->disconnect;
        $dbh2->disconnect;
        $dbh3->disconnect;
        $dbh4->disconnect;

        my $ans="Занятия удалены успешно!";
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
        my $ans="Вы не имеете права удалять занятия в группе!";
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
