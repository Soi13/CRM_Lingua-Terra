#!/usr/bin/perl -w
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
use Net::SMTP;
use Net::SMTP_auth;



use Log::Any qw($log);
use Log::Any::Adapter ('Stdout');
use Log::Any::Adapter ('File', 'file.log');
use Log::Any::For::Std;


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
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:a0018982_fin",User=>"a0018982_oleg", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
 
        my $feedback=param('FEEDBACK');
        my $topic_id=param('topic_id'); 
        my $topic_name=param('topic_name');
        my $date_lesson=param('date_lesson');         
                
        $feedback=~s/\0//g; $feedback=~s/\.\.//g; $feedback=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs; 
        $feedback=~s/<script>(.*[\s\S]*?)\<\/script>//gs; #Удаление текста между тегами Script
        $feedback=~s/<script>|<\/script>|script|\/script//gs; #Удаление самих тегов Script
        $topic_id=~s/\0//g; $topic_id=~s/\.\.//g; $topic_id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $topic_name=~s/\0//g; $topic_name=~s/\.\.//g; $topic_name=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $date_lesson=~s/\0//g; $date_lesson=~s/\.\.//g; $date_lesson=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($feedback,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        Encode::from_to($topic_name,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        
        ########Проверка на ввод текста отзыва
        if (length($feedback)==0)
        {
          my $ans="Необходимо заполнить текст отзыва!";
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
        
        #Определяем наименование группы, ФИО препода и ФИО студента
        my $data;
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select groups.GROUP_NAME, teachers.FIO, pupils.FIO from groups, groups_students, teachers, lessons, pupils where groups.ID=groups_students.GROUP_ID and groups.ID=lessons.GROUP_ID and teachers.ID=lessons.TEACHER_ID and groups_students.PUPILS_NUM_DOGOVOR=pupils.Num_dogovor and groups_students.PUPILS_NUM_DOGOVOR=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($num_dog);
        my @row_dat = $sth->fetchrow_array;
        #################################################
        
        #Добавляем отзыв
        my $dbh7=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth7=$dbh7->do("SET NAMES 'cp1251'");
        my $sql7="insert into feedback_lessons (ID_TOPIC_HOMEWORK, PUPILS_NUM_DOGOVOR, TEXT_FEEDBACK, DATETIME_CREATE) values (?,?,?, NOW())";
        $sth7=$dbh7->prepare($sql7);
        $sth7->execute($topic_id, $num_dog, $feedback);    
        
        my $smtp = Net::SMTP_auth->new('smtp.lingua-terra.ru', Timeout => 20, Debug => 1, Port=>587) or die "Couldn't connect to server; $!"; 
        $smtp->auth('LOGIN','robot@lingua-terra.ru','lingua');
        $smtp->mail('robot@lingua-terra.ru');
        my @to = qw(skvortsov@lingua-terra.ru school@lingua-terra.ru);
        foreach my $rcpt (@to)
        {
          $smtp->to($rcpt);
        }
        $smtp->data();
        $smtp->datasend("Subject: Отзыв о занятии\n");
        $smtp->datasend("To: skvortsov\@lingua-terra.ru\n");
        $smtp->datasend("From: robot\@lingua-terra.ru\n");
        $smtp->datasend("Content-Type: text/html; charset=\"windows-1251\"\n\n");
        $smtp->datasend("\n");
        $smtp->datasend("Отзыв от <b>", $row_dat[2], "</b> о занятии <b>", $date_lesson, "</b>, тема: <b>", $topic_name,"</b>. Группа: <b>", $row_dat[0], "</b>, преподаватель: <b>", $row_dat[1]), "</b>. ";
        $smtp->datasend("\n\n");
        $smtp->datasend("\n\n");                
        $smtp->datasend("<font color=\"blue\">", $feedback, "</font>");
        $smtp->datasend("\n");
        $smtp->quit; 
    
        my $ans="Отзыв успешно добавлен и отправлен!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
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
       my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
       print "Set-Cookie: $cookies\n";
       #Удаляем сессию
       $sess->delete();
       $sess->flush();
      }
}
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }
#############################################################

__END__
