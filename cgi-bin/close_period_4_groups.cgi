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

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $us_id=$sess->param('USER_ID');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my @data=param('dat'); #�������� ID ��������� �����

if (scalar(@data)==0)
{
  my $ans="�� ������� ������ ��� �������� �������������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}  

foreach my $ch (@data)
{
        $ch=~s/\0//g;
        $ch=~s/\.\.//g;
        $ch=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
}

my @debtor_students;   #����� ��� ���������� ��������� ���������, ��� ������� ������ ��������� ������� ������������� ���

#���� �� ���� ������� � � ������ ������ ������� ���������, ������� ��������� � ���� ������ � ������������ ���� ���������.
foreach my $gr (@data)
{
   #�������� ���� ���������, ������� ����������� � ������������ � ����� ������
   my $data1;
   my @list_students;
   my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth=$dbh->do("SET NAMES 'cp1251'");
   my $sql="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
   $sth=$dbh->prepare($sql);
   $sth->execute($gr);
   #� ������ ���������� ����������� ������
   while ($data1=$sth->fetchrow_array) {
   push  @list_students, $data1; 
   }
   ################################################       
  
   #� ����� ���� �� ����������� ������ ��������� � ������ � ������������ �� ��� �������� �������������� ����
   foreach my $student_dogovor (@list_students)
   {
      ##############################����������, ���� �� �� ���������� �������� �� ���������� ������ � �� �������� �� �� ���������. ���� ����, ������ �� ������� � ����������� �������� �������������� ���� ��� ���� ������!
      my $dbh0=ConnectDB->connect;
      my $sth0=$dbh0->do("SET NAMES 'cp1251'");
      my $sql0="select * from pays where opl_summ=0 and pupils_num_dogovor=?";
      $sth0=$dbh0->prepare($sql0); #��� �������� ������� �� ���������� ��������
      $sth0->execute($student_dogovor);
      my @zero_opl = $sth0->fetchrow_array; 
      ############################################################################### 
      
      ##############################����������, ���� �� �� ���������� �������� �� ����������� ������. ���� ����, ������ �� ������� � � ����� ���������� ������.
      my $dbh1=ConnectDB->connect;
      my $sth1=$dbh1->do("SET NAMES 'cp1251'");
      my $sql1="select * from pays where opl_summ<>0 and opl_summ<summ_4_opl and pupils_num_dogovor=?";
      $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
      $sth1->execute($student_dogovor);
      my @non_opl = $sth1->fetchrow_array; 
      ###############################################################################
            
      #���� � �������� ���� ������������ ��� ������������� �����, �� ������� ������ �������� � ����. �����, ����� � ����� ��������� ����� ������� ������ ���������, ������� �� ������� ������� ������������� ���.
      if (@zero_opl || @non_opl)
      {
         ##############################����������, ��� �������� �� ��� ������ �������
         my $dbh2=ConnectDB->connect;
         my $sth2=$dbh2->do("SET NAMES 'cp1251'");
         my $sql2="select FIO from pupils where Num_dogovor=?";
         $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
         $sth2->execute($student_dogovor);
         my @fio_stud = $sth2->fetchrow_array; 
         ############################################################################### 
         
         #��������� � ������ ��������� � ��� ��������-��������
         push @debtor_students, "<br /> ".$student_dogovor."-".$fio_stud[0];     
         
         next;   
      }
      ##################################################################################
      
      
      #���� � �������� ��� ������, �� ������������ ��������� �������� �������������� ���� ��� ����
      #���������� ������ � ����� ������� (������) ��������
      my $data2;
      my @period_study;
      my $dbh3=ConnectDB->connect;
      my $sth3=$dbh3->do("SET NAMES 'cp1251'");
      my $sql3="select PERIOD from pays where pupils_num_dogovor=? and ID=(select min(ID) from pays where pupils_num_dogovor=?) or ID=(select max(ID) from pays where pupils_num_dogovor=?)";
      $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
      $sth3->execute($student_dogovor, $student_dogovor, $student_dogovor);
      #� ������ ���������� ����������� ������
      while ($data2=$sth3->fetchrow_array) {
      push @period_study, $data2; 
      }
      ############################################################################### 
    
      ###################################���������� UUID ��� ���������� �� ���� ������ �� � ������� ������ ����� �������� �� 3-� ������
      my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth4=$dbh4->do("SET NAMES 'cp1251'");
      my $sql4="select UUID()";
      $sth4=$dbh4->prepare($sql4);
      $sth4->execute();
      my @row_uuid = $sth4->fetchrow_array;
      ################################################
      
      #���������� �������� ������, �������� ��������� �������� � �����, ��� �������, ������
      my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth5=$dbh5->do("SET NAMES 'cp1251'");
      my $sql5="select groups.GROUP_NAME, kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, teachers.FIO as TEACHER_FIO, branches.BRANCH from groups, kind_languages, kind_programm, teachers, lessons, branches where teachers.ID=lessons.TEACHER_ID and lessons.GROUP_ID=groups.ID and groups.LANGUAGE=kind_languages.ID and groups.KIND_PROGRAMM=kind_programm.ID and groups.BRANCH=branches.ID and groups.ID=?";
      $sth5=$dbh5->prepare($sql5);
      $sth5->execute($gr);
      my @groups_data = $sth5->fetchrow_array;
      ################################################
      
      #############�� ������ �������� �������� �������� ��� ��� ������
      my $data3;
      my @pays_student;
      my $dbh7=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth7=$dbh7->do("SET NAMES 'cp1251'");   
      my $sql7="select PERIOD, SUMM_4_OPL, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES from pays where PUPILS_NUM_DOGOVOR=?";
      $sth7=$dbh7->prepare($sql7); #��� �������� ������� �� ���������� ��������
      $sth7->execute($student_dogovor);
      while ($data3=$sth7->fetchrow_hashref) {
      push @pays_student, $data3;
      }
      
      #############�� ������ �������� �������� �������� ��� ��������� �������� ��� �� �������� � �����
      my $data5;
      my @doc_students;
      my $dbh10=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth10=$dbh10->do("SET NAMES 'cp1251'");         
      my $sql10="select type_doc.NAME_DOC, kind_programm.NAME_PROGRAMM, type_groups.GROUPS, document_students.PRICE_COURSE, document_students.DATE_START_DOGOVOR, document_students.DATE_END_DOGOVOR, document_students.TEXT_DOCUM, document_students.USER_ID, document_students.DATETIME_CREATE, document_students.ID from document_students, type_doc, kind_programm, type_groups where document_students.TYPE_DOC=type_doc.ID and document_students.COURSE=kind_programm.ID and document_students.TYPE_GROUP=type_groups.ID and document_students.DATETIME_CREATE<STR_TO_DATE( (select datetime_create from document_students where id=(select max(id) from document_students where pupils_num_dogovor=?)), '%Y-%m-%d %H:%i:%s') and PUPILS_Num_dogovor=?";      
	  #my $sql10="select type_doc.NAME_DOC, kind_programm.NAME_PROGRAMM, type_groups.GROUPS, document_students.PRICE_COURSE, document_students.DATE_START_DOGOVOR, document_students.DATE_END_DOGOVOR, document_students.TEXT_DOCUM, document_students.USER_ID, document_students.DATETIME_CREATE from document_students, type_doc, kind_programm, type_groups where document_students.TYPE_DOC=type_doc.ID and document_students.COURSE=kind_programm.ID and document_students.TYPE_GROUP=type_groups.ID and year(document_students.DATE_START_DOGOVOR)<year(now()) and PUPILS_Num_dogovor=?";
      $sth10=$dbh10->prepare($sql10); #��� �������� ������� �� ���������� ��������
      $sth10->execute($student_dogovor, $student_dogovor);
      while ($data5=$sth10->fetchrow_hashref) {
      push @doc_students, $data5;
      }
	  
	  #############�� ������ �������� �������� �������� ��� ��� ������
      my $data6;
      my @ord_students;
      my $dbh15=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth15=$dbh15->do("SET NAMES 'cp1251'");   
      my $sql15="select orders.ID, orders.TYPE_DOC, orders.DATE_PAY, orders.PUPILS_NUM_DOGOVOR_OR_KA, orders.OSNOVANIE, orders.SUMM_OPL, orders.STATUS, usr.FULL_NAME as MADE_ORDER from orders, usr where orders.USER_ID=usr.ID and orders.PUPILS_NUM_DOGOVOR_OR_KA=?";
      $sth15=$dbh15->prepare($sql15); #��� �������� ������� �� ���������� ��������
      $sth15->execute($student_dogovor);
      while ($data6=$sth15->fetchrow_hashref) {
      push @ord_students, $data6;
      }
	  
	  #############�� ������ �������� �������� �������� ��� ��������� �������
      my $data7;
      my @visits_students;
      my $dbh16=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth16=$dbh16->do("SET NAMES 'cp1251'");   
      my $sql16="select PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES from visits where PUPILS_NUM_DOGOVOR=?";
      $sth16=$dbh16->prepare($sql16); #��� �������� ������� �� ���������� ��������
      $sth16->execute($student_dogovor);
      while ($data7=$sth16->fetchrow_hashref) {
      push @visits_students, $data7;
      }

      #############�� ID ������ �������� ��� �� �������� �������������� ���� ������
      my $data8;
      my @topic_homework_students;   
      my $dbh17=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth17=$dbh17->do("SET NAMES 'cp1251'");   
      my $sql17="select PERIOD, DATE_LESSON, TOPIC, HOME_WORK from topic_homework where GROUP_ID=?";
      $sth17=$dbh17->prepare($sql17); #��� �������� ������� �� ���������� ��������
      $sth17->execute($gr);
      while ($data8=$sth17->fetchrow_hashref) {
      push @topic_homework_students, $data8;
      }

      #���������� �������� �� � ������ �� ������� ����������� ������ ������ ��������, ����� �������� ��� �������� ��������� ������ ���. ���� ��������, �� ������� ������ � �� �� ������� ������, �.�. ��� ����� ��� ������ ����������� ���������. ���� �� �� �������� � ������� ������� ���������, �� ������ ����� �������.
      my $dbh18=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth18=$dbh18->do("SET NAMES 'cp1251'");      
      my $sql18="select pupils_num_dogovor from groups_students where group_id=? and pupils_num_dogovor not like ?";
      $sth18=$dbh18->prepare($sql18);
      $sth18->execute($gr, $student_dogovor);
      my @exist_stud = $sth18->fetchrow_array;
      ################################################
	  
	  #############�� ������ �������� �������� ��� ������ �������� �� ���� ��������
      my $data9;
      my @feedback_students;   
      my $dbh19=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth19=$dbh19->do("SET NAMES 'cp1251'");   
      my $sql19="select topic_homework.TOPIC, feedback_lessons.TEXT_FEEDBACK from topic_homework, feedback_lessons where topic_homework.ID=feedback_lessons.ID_TOPIC_HOMEWORK and feedback_lessons.PUPILS_NUM_DOGOVOR=?";
      $sth19=$dbh19->prepare($sql19); #��� �������� ������� �� ���������� ��������
      $sth19->execute($student_dogovor);
      while ($data9=$sth19->fetchrow_hashref) {
      push @feedback_students, $data9;
      }
    
      #���������� ������� ������ � �������� �������� ������. ���� ��� �������� � �������
      #���������� ����� ���������� � ���� Eval � ���������� $@, ���� ��������� ������ �� ����� ���������� SQL ������ � ����� Eval, �� ��������� ����� ��������
      my $dbh6=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
      my $sth6=$dbh6->do("SET NAMES 'cp1251'");
      eval {
        
         
         #��������� ���������/������ � ������� ������� . ��� ����� �������� �������� ������������� ��� �������� � GUID �������� ��� ����� � ������� ���������.
         my $sql6="insert into past_academ_years (PUPILS_NUM_DOGOVOR, PERIOD, UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,NOW())";
         $sth6=$dbh6->prepare($sql6);
         $sth6->execute($student_dogovor, $period_study[0]." - ".$period_study[1], $row_uuid[0], $us_id);
         ###############################################################
        
        
         #��������� ������ � ������ �������� � ������� �� ��������. ����� � ������� ��������� ����� ����������� �� GUID ����         
         if (@groups_data)
         {
           $sql6="insert into past_academ_years_group_data (GROUP_NAME, LANGUAGE, PROGRAMM_NAME, TEACHER_FIO, BRANCH, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,NOW())";
           $sth6=$dbh6->prepare($sql6);
           $sth6->execute($groups_data[0], $groups_data[1], $groups_data[2], $groups_data[3], $groups_data[4], $row_uuid[0], $us_id);
         }
         ###############################################################

         
         #��������� ������� �������� ����� ��������� �������� ����. ��� ����� ����� ������ �� ������� ��������� �������� � ��������� �� � �������
         if (@pays_student)
         {
            for (my $c=0; $c<=$#pays_student; $c++)
            {
               $sql="insert into past_academ_years_pays (PERIOD, SUMM_4_OPL, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,NOW())";
               $sth=$dbh->prepare($sql);
               $sth->execute($pays_student[$c]->{"PERIOD"}, $pays_student[$c]->{"SUMM_4_OPL"}, $pays_student[$c]->{"OPL_SUMM"}, $pays_student[$c]->{"DATE_OF_PAY"}, $pays_student[$c]->{"STATUS"}, $pays_student[$c]->{"NOTES"}, $row_uuid[0], $us_id);
            }
         }
         ###############################################################
         
         if (@doc_students)
         {
            #����� ������ �� ������� ��������� ���������� � ��������� �� � �����
            for (my $d=0; $d<=$#doc_students; $d++)
            {
               $sql="insert into past_academ_years_documents (TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,NOW())";
               $sth=$dbh->prepare($sql);
               $sth->execute($doc_students[$d]->{"NAME_DOC"}, $doc_students[$d]->{"NAME_PROGRAMM"}, $doc_students[$d]->{"GROUPS"}, $doc_students[$d]->{"PRICE_COURSE"}, $doc_students[$d]->{"DATE_START_DOGOVOR"}, $doc_students[$d]->{"DATE_END_DOGOVOR"}, $doc_students[$d]->{"TEXT_DOCUM"}, $row_uuid[0], $us_id);
            }            
         }
         ###############################################################
		 
		 if (@ord_students)
         {
            #����� ������ �� ������� ��������� ������� � ��������� �� � �����
            for (my $a=0; $a<=$#ord_students; $a++)
            {
               $sql="insert into past_academ_years_orders (NUM_ORDER, TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, PAST_ACADEM_YEARS_UUID, USER_CREATED_ORDER, USER_ID, DATETIME_CREATE, STATUS) values (?,?,?,?,?,?,?,?,?,NOW(),?)";
               $sth=$dbh->prepare($sql);
               $sth->execute($ord_students[$a]->{"ID"}, $ord_students[$a]->{"TYPE_DOC"}, $ord_students[$a]->{"DATE_PAY"}, $ord_students[$a]->{"PUPILS_NUM_DOGOVOR_OR_KA"}, $ord_students[$a]->{"OSNOVANIE"}, $ord_students[$a]->{"SUMM_OPL"}, $row_uuid[0], $ord_students[$a]->{"MADE_ORDER"}, $us_id, $ord_students[$a]->{"STATUS"});
            }            
         }
         ###############################################################
		 
		 if (@visits_students)
         {
            #����� ������ �� ������� ��������� ��������� � ��������� �� � �����
            for (my $s=0; $s<=$#visits_students; $s++)
            {
               $sql6="insert into past_academ_years_visits (PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW())";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute($visits_students[$s]->{"PERIOD"}, $visits_students[$s]->{"DAY1"}, $visits_students[$s]->{"DAY2"}, $visits_students[$s]->{"DAY3"}, $visits_students[$s]->{"DAY4"}, $visits_students[$s]->{"DAY5"}, $visits_students[$s]->{"DAY6"}, $visits_students[$s]->{"DAY7"}, $visits_students[$s]->{"DAY8"}, $visits_students[$s]->{"DAY9"}, $visits_students[$s]->{"DAY10"}, $visits_students[$s]->{"DAY11"}, $visits_students[$s]->{"DAY12"}, $visits_students[$s]->{"DAY13"}, $visits_students[$s]->{"DAY14"}, $visits_students[$s]->{"DAY15"}, $visits_students[$s]->{"DAY16"}, $visits_students[$s]->{"DAY17"}, $visits_students[$s]->{"DAY18"}, $visits_students[$s]->{"DAY19"}, $visits_students[$s]->{"DAY20"}, $visits_students[$s]->{"DAY21"}, $visits_students[$s]->{"DAY22"}, $visits_students[$s]->{"DAY23"}, $visits_students[$s]->{"DAY24"}, $visits_students[$s]->{"DAY25"}, $visits_students[$s]->{"DAY26"}, $visits_students[$s]->{"DAY27"}, $visits_students[$s]->{"DAY28"}, $visits_students[$s]->{"DAY29"}, $visits_students[$s]->{"DAY30"}, $visits_students[$s]->{"DAY31"}, $visits_students[$s]->{"NOTES"}, $row_uuid[0], $us_id);
            }            
         }
         ###############################################################

         if (@topic_homework_students)
         {
            #����� ������ �� ������� ��������� �� � ��������� �� � �����
            for (my $f=0; $f<=$#topic_homework_students; $f++)
            {
               $sql6="insert into past_academ_years_topic_homework (PERIOD, DATE_LESSON, TOPIC, HOME_WORK, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,NOW())";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute($topic_homework_students[$f]->{"PERIOD"}, $topic_homework_students[$f]->{"DATE_LESSON"}, $topic_homework_students[$f]->{"TOPIC"}, $topic_homework_students[$f]->{"HOME_WORK"}, $row_uuid[0], $us_id);               
            }            
         }
         ###############################################################
		 
		 if (@feedback_students)
         {
            #����� ������ �� ������� ��������� ������� � ��������� �� � �����
            for (my $j=0; $j<=$#feedback_students; $j++)
            {
               $sql6="insert into past_academ_years_feedback_lessons (TOPIC, TEXT_FEEDBACK, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,NOW())";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute($feedback_students[$j]->{"TOPIC"}, $feedback_students[$j]->{"TEXT_FEEDBACK"}, $row_uuid[0], $us_id);               
            }            
         }
         ###############################################################

         #�������� �������� ��������
         $sql="delete from pays where pupils_num_dogovor=?";
         $sth=$dbh->prepare($sql);
         $sth->execute($student_dogovor);
  
         #�������� ���������� ��������
		 if (@doc_students)
         {
           #����� ������ �� ������� ��������� ���������� � ��������� �� � �����
           for (my $d1=0; $d1<=$#doc_students; $d1++)
           {
             $sql="delete from document_students where document_students.ID=?";
             $sth=$dbh->prepare($sql);
             $sth->execute($doc_students[$d1]->{"ID"});
		   }
         }		   
  
         #�������� ������� ��������� �������� (���������� �������)
         $sql="delete from calendar_pupils where PUPILS_NUM_DOGOVOR=?";
         $sth=$dbh->prepare($sql);
         $sth->execute($student_dogovor);    

         #�������� ������� ��������
         $sql="delete from orders where PUPILS_NUM_DOGOVOR_OR_KA=?";
         $sth=$dbh->prepare($sql);
         $sth->execute($student_dogovor); 		 
  
         #�������� �������� �������� �� ������
         $sql="delete from groups_students where PUPILS_NUM_DOGOVOR=?";
         $sth=$dbh->prepare($sql);
         $sth->execute($student_dogovor);
		 
		 #�������� ��������� ��������
         $sql6="delete from visits where PUPILS_NUM_DOGOVOR=?";
         $sth6=$dbh6->prepare($sql6);
         $sth6->execute($student_dogovor);
        
         #�������� �� ��������
         if (!@exist_stud)
         {           
           $sql6="delete from topic_homework where GROUP_ID=?";
           $sth6=$dbh6->prepare($sql6);
           $sth6->execute($gr);
         }
		 
		 #�������� ������� ��������
         $sql6="delete from feedback_lessons where PUPILS_NUM_DOGOVOR=?";
         $sth6=$dbh6->prepare($sql6);
         $sth6->execute($student_dogovor);
           
          
         $dbh6->commit; #���������� ����������
         $dbh6->{AutoCommit}=1; 
         $dbh6->{RaiseError}=0;  
      };
      if ($@) # ���� ��������� ������, �� ���������� ����������
      {
         # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
         eval { $dbh6->rollback; };
      }     
          
   }


   #����� ��������� ���� ��������� � ������� ������, �������� ��� ���� �� ��������� ������ �������� ������ ���. ���� ��� ����, ������ �� � ������ ��� � ������ ����� �������, ���� ��� � ���-�� �� ��������� ������� (�.�. �� �������), �� ������� ������ ������!!!
   my $data4;
   my @exist_stud_in_group;
   my $dbh8=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth8=$dbh8->do("SET NAMES 'cp1251'");
   my $sql8="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
   $sth8=$dbh8->prepare($sql8);
   $sth8->execute($gr);
   while ($data4=$sth8->fetchrow_hashref) {
   push @exist_stud_in_group, $data4;
   }
   ################################################

   if (!@exist_stud_in_group)
   {
      #����������� UUID � ������� lessons, ������� ��������� � ������ ��� �������� ��������� � ������ ������� � ������
      my $dbh12=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth12=$dbh12->do("SET NAMES 'cp1251'");
      my $sql12="select UUID from lessons where GROUP_ID=?";
      $sth12=$dbh12->prepare($sql12);
      $sth12->execute($gr);
      my @lessons_uuid = $sth12->fetchrow_array;
      
      #�������� ��������� ������ �� ������� lessons_group
      my $dbh13=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth13=$dbh13->do("SET NAMES 'cp1251'");
      my $sql13="delete from lessons_group where UUID_LESSONS=?";
      $sth13=$dbh13->prepare($sql13);
      $sth13->execute($lessons_uuid[0]); 
      
      #�������� ������ ������� ������ �� ������� lessons_list
      my $dbh14=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth14=$dbh14->do("SET NAMES 'cp1251'");
      my $sql14="delete from lessons_list where UUID_LESSONS=?";
      $sth14=$dbh14->prepare($sql14);
      $sth14->execute($lessons_uuid[0]); 
            
      #�������� ������ �� ������� groups
      my $dbh9=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth9=$dbh9->do("SET NAMES 'cp1251'");
      my $sql9="delete from groups where ID=?";
      $sth9=$dbh9->prepare($sql9);
      $sth9->execute($gr);           
   }
   else
   {
      #������������� ������ ������, ����� ��� � ������ ������������ ������� ������, ����� ����� ����, ��� � ��� ���� �������� ����� �������� �������� ����
      my $dbh11=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth11=$dbh11->do("SET NAMES 'cp1251'");
      my $sql11="update groups set DEBTS_STUDENT=1 where ID=?";
      $sth11=$dbh11->prepare($sql11);
      $sth11->execute($gr);  
   }  
   
  
}


if (@debtor_students)
{
  my @debtors_4_file=@debtor_students;
   #������ � ���� ��������� ��� ������� ���������� ���������� �������� �������������� ����
   my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
   $year+=1900;
   open (REG, ">>../reports/academ_".$year.$mon.$mday.$hour.$min.$sec.".rtf") or die "������ ������� ���� messages.dat: $!";
   $/="**";
   foreach my $str (@debtors_4_file)
   {
     $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//im; #������� � ������ ��� ��� <br />   
     print REG $str;
     print REG "\n";
   }
   close (REG) or die $!;
   
   push @debtor_students, "<br /><a href=\"../reports/academ_$year$mon$mday$hour$min$sec.rtf\">������� ���� � �������������� ���</a>";
   
   my $res_str=join(",", @debtor_students);   
   
   my $ans="<b>��� ������������� ��������� ���������� ������� ������� ������������� ���, �.�. � ��� ������� ���������!</b> <br />".$res_str;
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;
   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});
   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   exit;   
     
}
else
{
   my $ans="��� ��������� ����� ������� ������������� ��� ������ �������!";
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;
   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});
   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   exit;
}


#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
