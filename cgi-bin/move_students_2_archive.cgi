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


#use Log::Any qw($log);
#use Log::Any::Adapter ('Stdout');
#use Log::Any::Adapter ('File', 'file.log');
#use Log::Any::For::Std;

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

my $data;
my @pays;
my @doc_students;
my @calend_pupils;
my @events_pupils;
my @history_stud;
my @opl_without_gr;
my @past_academ_years;
my @past_academ_years_documents;
my @past_academ_years_groups;
my @past_academ_years_orders;
my @past_academ_years_pays;
my @past_academ_years_visits;
my @past_academ_years_homework;
my @past_academ_years_feedback;
my @group_stud;
my @row_pupil;
my @zero_opl;
my @underpayment;
my @underpayment_part;
my @visits_stud;
my @homework_stud;
my @feedback_stud;
my @group_id;


#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
  
  my @data=param('dat');

  if (scalar(@data)==0)
  {
    my $ans="�� ������� �������� ��� �������� � �����!";
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

  ##############################����������, ���� �� �� ���������� �������� �� ���������� ������ � �� �������� �� �� ���������. ���� ����, ������ �� ������� � � ����� ���������� ������. ���� �� ������� �� �������� ��������� � ������ ������� ��������, �� ���������� ������� �������� ������� � ����� ���������� � �����.
  for (my $t=0; $t<=$#data; $t++)
  {  
    my $dbh0=ConnectDB->connect;
    my $sth0=$dbh0->do("SET NAMES 'cp1251'");
    my $sql0="select * from pays where opl_summ=0 and pupils_num_dogovor=?";
    $sth0=$dbh0->prepare($sql0); #��� �������� ������� �� ���������� ��������
    $sth0->execute($data[$t]);
    my @zero_opl = $sth0->fetchrow_array; 
    $dbh0->disconnect;     
    
    if (@zero_opl)
    {
      push @underpayment, $data[$t];    
    }
  }
  
  if (@underpayment)
  {
      my $str_underpayment = join(", ", @underpayment);
      my $ans="����������� � ����� ���������� ��� ��������� ���������: <b>".$str_underpayment."</b>. <br /> � ��� ������� ������������ �����! ���� ��� �� �����, ��������, �� ��������� ��������, �� ������ ������� ���������� ������� ����� ������������ � �����."; 
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json; 
      exit;
  }
  ##################################################################################
  
 
  ##############################����������, ���� �� �� ���������� �������� �� ����������� ������. ���� ����, ������ �� ������� � � ����� ���������� ������.
  for (my $y=0; $y<=$#data; $y++)
  {
    my $dbh1=ConnectDB->connect;
    my $sth1=$dbh1->do("SET NAMES 'cp1251'");
    my $sql1="select * from pays where opl_summ<>0 and opl_summ<summ_4_opl and pupils_num_dogovor=?";
    $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
    $sth1->execute($data[$y]);
    my @non_opl = $sth1->fetchrow_array; 
    $dbh1->disconnect;
  
    if (@non_opl)
    {
      push @underpayment_part, $data[$y];      
    }
  }
  
  if (@underpayment_part)
  {
    my $str_underpayment_part = join(", ", @underpayment_part);
    my $ans="����������� � ����� ���������� ��� ��������� ���������: <b>".$str_underpayment_part."</b>. <br />� ��� ������ ������������� �����!"; 
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json; 
    exit;
  }
  ##################################################################################
  

  ################################### �� ������ �������� ���������� � �������� ���������� �� ���������� �������� � ��������� �� � ����� �� �������, � �������� archive, ����� ��� ���� ����� ������������ � ������.
 
  ###################################��������� ������ �� ������ � ������� zayavki_reserv � ����� ������� ������ �� ������� zayavki
  #���������� ����� ���������� � ���� Eval � ���������� $@, ���� ��������� ������ �� ����� ���������� SQL ������ � ����� Eval, �� ��������� ����� ��������
  my $dbh=DBI->connect("DBI:mysql:spending", "root", "89302810", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  for (my $u=0; $u<=$#data; $u++)
  {
    eval {  
        
            #############�� ������ �������� �������� �������� ��� ������� �������� ��� �� �������� � �����
            my $sql="select * from pays where opl_summ>0 and pupils_num_dogovor=?";
            $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
            $sth->execute($data[$u]);
            while ($data=$sth->fetchrow_hashref) {
            push @pays, $data;
            }
 
            if (@pays)
            {
              #����� ������ �� ������� ��������� ����� � ��������� �� � �����  
              for (my $p=0; $p<=$#pays; $p++)
              {
                 $sql="insert into pays_archive (PUPILS_NUM_DOGOVOR, PERIOD, SUMM_4_OPL, OPL_SUMM, DATE_OF_PAY, STATUS, GROUP_ID, NOTES, USER_ID, DATETIME_CREATE, SUMM_ORDER) values (?,?,?,?,?,?,?,?,?,NOW(),?)";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($pays[$p]->{"PUPILS_NUM_DOGOVOR"}, $pays[$p]->{"PERIOD"}, $pays[$p]->{"SUMM_4_OPL"}, $pays[$p]->{"OPL_SUMM"}, $pays[$p]->{"DATE_OF_PAY"}, $pays[$p]->{"STATUS"}, $pays[$p]->{"GROUP_ID"}, $pays[$p]->{"NOTES"}, $us_id, $pays[$p]->{"SUMM_ORDER"});
              }
              ################################################################################################
            }

            #############�� ������ �������� �������� �������� ��� ��������� �������� ��� �� �������� � �����
            #$sql="select * from document_students where PUPILS_Num_dogovor=?";
            $sql="select document_students.PUPILS_Num_dogovor, type_doc.NAME_DOC, kind_programm.NAME_PROGRAMM, type_groups.GROUPS, document_students.PRICE_COURSE, document_students.DATE_START_DOGOVOR, document_students.DATE_END_DOGOVOR, document_students.TEXT_DOCUM, document_students.USER_ID, document_students.DATETIME_CREATE from document_students, type_doc, kind_programm, type_groups where document_students.TYPE_DOC=type_doc.ID and document_students.COURSE=kind_programm.ID and document_students.TYPE_GROUP=type_groups.ID and PUPILS_Num_dogovor=?";
            $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
            $sth->execute($data[$u]);
            while ($data=$sth->fetchrow_hashref) {
            push @doc_students, $data;
            }
 
            if (@doc_students)
            {
               #����� ������ �� ������� ��������� ���������� � ��������� �� � �����
               for (my $d=0; $d<=$#doc_students; $d++)
               {
                  $sql="insert into document_students_archive (PUPILS_Num_dogovor, TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,NOW())";
                  $sth=$dbh->prepare($sql);
                  $sth->execute($doc_students[$d]->{"PUPILS_Num_dogovor"}, $doc_students[$d]->{"NAME_DOC"}, $doc_students[$d]->{"NAME_PROGRAMM"}, $doc_students[$d]->{"GROUPS"}, $doc_students[$d]->{"PRICE_COURSE"}, $doc_students[$d]->{"DATE_START_DOGOVOR"}, $doc_students[$d]->{"DATE_END_DOGOVOR"}, $doc_students[$d]->{"TEXT_DOCUM"}, $us_id);
               }
               ################################################################################################
             }
  
             #############�� ������ �������� �������� �������� ��� ��� ������� � ��������� (���������� �������) ��� �� �������� � �����
             $sql="select * from calendar_pupils where PUPILS_NUM_DOGOVOR=?";
             $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
             $sth->execute($data[$u]);
             while ($data=$sth->fetchrow_hashref) {
             push @calend_pupils, $data;
             }
 
             if (@calend_pupils)
             {
                #����� ������ �� ������� ��������� ������� ��������� � ��������� �� � �����
                for (my $c=0; $c<=$#calend_pupils; $c++)
                {
                   $sql="insert into calendar_pupils_archive (START_DATE, END_DATE, TEXT_MESSAGE, DETAILS, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,NOW())";
                   $sth=$dbh->prepare($sql);
                   $sth->execute($calend_pupils[$c]->{"START_DATE"}, $calend_pupils[$c]->{"END_DATE"}, $calend_pupils[$c]->{"TEXT_MESSAGE"}, $calend_pupils[$c]->{"DETAILS"}, $calend_pupils[$c]->{"PUPILS_NUM_DOGOVOR"}, $calend_pupils[$c]->{"GROUP_ID"}, $calend_pupils[$c]->{"UUID_LESSONS"}, $us_id);
                }
                ################################################################################################
              }
			  
			 #############�� ������ �������� �������� �������� ��� ���������� ����������� �������� ��� �� �������� � �����
             $sql="select events_pupils.PUPILS_NUM_DOGOVOR, events_pupils.DATE_VISIT, events.NAME_EVENT, events_pupils.FEEDBACK from events_pupils, events where events_pupils.KIND_EVENT=events.ID and events_pupils.PUPILS_NUM_DOGOVOR=?";
             $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
             $sth->execute($data[$u]);
             while ($data=$sth->fetchrow_hashref) {
             push @events_pupils, $data;
             }
 
             if (@events_pupils)
             {
                #����� ������ �� ������� ��������� ����������� � ��������� �� � �����
                for (my $z=0; $z<=$#events_pupils; $z++)
                {
                   $sql="insert into events_pupils_archive (PUPILS_NUM_DOGOVOR, DATE_VISIT, KIND_EVENT, FEEDBACK, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,NOW())";
                   $sth=$dbh->prepare($sql);
                   $sth->execute($events_pupils[$z]->{"PUPILS_NUM_DOGOVOR"}, $events_pupils[$z]->{"DATE_VISIT"}, $events_pupils[$z]->{"NAME_EVENT"}, $events_pupils[$z]->{"FEEDBACK"}, $us_id);
                }
                ################################################################################################
             }

              #############�� ������ �������� �������� �������� ��� ��� ������ �� ��� ������� ��� �� �������� � �����
              $sql="select * from history_students where PUPILS_NUM_DOGOVOR=?";
              $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
              $sth->execute($data[$u]);
              while ($data=$sth->fetchrow_hashref) {
              push @history_stud, $data;
              }
 
              if (@history_stud)
              {
                 #����� ������ �� ������� ��������� ������� � ������� � ��������� �� � �����
                 for (my $h=0; $h<=$#history_stud; $h++)
                 {
                    $sql="insert into history_students_archive (PUPILS_NUM_DOGOVOR, TEXT, NOTES, DATETIME_CREATE, USER_ID) values (?,?,?,NOW(),?)";
                    $sth=$dbh->prepare($sql);
                    $sth->execute($history_stud[$h]->{"PUPILS_NUM_DOGOVOR"}, $history_stud[$h]->{"TEXT"}, $history_stud[$h]->{"NOTES"}, $us_id);
                 }
                 ################################################################################################
               }
			   
			   #############�� ������ �������� �������� �������� ��� ������������ ������ �������� ��� �� �������� � �����
               $sql="select PUPILS_NUM_DOGOVOR, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES from pays_without_group where PUPILS_NUM_DOGOVOR=?";
               $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
               $sth->execute($data[$u]);
               while ($data=$sth->fetchrow_hashref) {
               push @opl_without_gr, $data;
               }
 
               if (@opl_without_gr)
               {
                  #����� ������ �� ������� ��������� ������������ ����� � ��������� �� � �����
                  for (my $x=0; $x<=$#opl_without_gr; $x++)
                  {
                     $sql="insert into pays_without_group_archive (PUPILS_NUM_DOGOVOR, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES,  USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,NOW())";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($opl_without_gr[$x]->{"PUPILS_NUM_DOGOVOR"}, $opl_without_gr[$x]->{"OPL_SUMM"}, $opl_without_gr[$x]->{"DATE_OF_PAY"}, $opl_without_gr[$x]->{"STATUS"}, $opl_without_gr[$x]->{"NOTES"}, $us_id);
                  }
                  ################################################################################################
               }

               #############�� ������ �������� �������� �������� ������ �� ��� ������ ��� �� �������� � �����
               #$sql="select groups_students.PUPILS_NUM_DOGOVOR, groups.GROUP_NAME, groups_students.PRICE_COURSE, groups_students.BEGIN_STUDY, kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.START_DATE, groups.END_DATE from groups_students, groups, kind_languages, kind_programm where groups_students.GROUP_ID=groups.ID and groups.LANGUAGE=kind_languages.ID and groups.KIND_PROGRAMM=kind_programm.ID and groups_students.PUPILS_NUM_DOGOVOR=?";
               $sql="select groups_students.PUPILS_NUM_DOGOVOR, groups.GROUP_NAME, groups_students.PRICE_COURSE, groups_students.BEGIN_STUDY, kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, teachers.FIO as TEACHER_FIO, groups.START_DATE, groups.END_DATE from groups_students, groups, kind_languages, kind_programm, teachers, lessons where teachers.ID=lessons.TEACHER_ID and lessons.GROUP_ID=groups.ID and groups_students.GROUP_ID=groups.ID and groups.LANGUAGE=kind_languages.ID and groups.KIND_PROGRAMM=kind_programm.ID and groups_students.PUPILS_NUM_DOGOVOR=?";  
               $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
               $sth->execute($data[$u]);
               while ($data=$sth->fetchrow_hashref) {
               push @group_stud, $data;
               }
 
               if (@group_stud)
               { 
                  #����� ������ �� ������� ��������� ������� � �������, ���� ������ � �������� ����� ���� ������ ����! �������, �� ����, ����� ���� �� �����.
                  for (my $g=0; $g<=$#group_stud; $g++)
                  {
                     $sql="insert into groups_students_archive (PUPILS_NUM_DOGOVOR, GROUP_NAME, PRICE_COURSE, BEGIN_STUDY, LANGUAGE, KIND_PROGRAMM, TEACHER_FIO, START_DATE, END_DATE, DATETIME_CREATE, USER_ID) values (?,?,?,?,?,?,?,?,?,NOW(),?)";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($group_stud[$g]->{"PUPILS_NUM_DOGOVOR"}, $group_stud[$g]->{"GROUP_NAME"}, $group_stud[$g]->{"PRICE_COURSE"}, $group_stud[$g]->{"BEGIN_STUDY"}, $group_stud[$g]->{"LANGUAGE"}, $group_stud[$g]->{"NAME_PROGRAMM"}, $group_stud[$g]->{"TEACHER_FIO"}, $group_stud[$g]->{"START_DATE"}, $group_stud[$g]->{"END_DATE"}, $us_id);
                  }
                  ################################################################################################
                }
				
				#############�� ������ �������� �������� �������� ��� ��� ��������� ��������
                $sql="select PUPILS_NUM_DOGOVOR, PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES from visits where PUPILS_NUM_DOGOVOR=?";
                $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                $sth->execute($data[$u]);
                while ($data=$sth->fetchrow_hashref) {
                push @visits_stud, $data;
                }
 
                if (@visits_stud)
                {
                   #����� ������ �� ������� ��������� ������� ��������� � ��������� �� � �����
                   for (my $k=0; $k<=$#visits_stud; $k++)
                   {
                      $sql="insert into visits_archive (PUPILS_NUM_DOGOVOR, PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW())";
                      $sth=$dbh->prepare($sql);
                      $sth->execute($visits_stud[$k]->{"PUPILS_NUM_DOGOVOR"}, $visits_stud[$k]->{"PERIOD"}, $visits_stud[$k]->{"DAY1"}, $visits_stud[$k]->{"DAY2"}, $visits_stud[$k]->{"DAY3"}, $visits_stud[$k]->{"DAY4"}, $visits_stud[$k]->{"DAY5"}, $visits_stud[$k]->{"DAY6"}, $visits_stud[$k]->{"DAY7"}, $visits_stud[$k]->{"DAY8"}, $visits_stud[$k]->{"DAY9"}, $visits_stud[$k]->{"DAY10"}, $visits_stud[$k]->{"DAY11"}, $visits_stud[$k]->{"DAY12"}, $visits_stud[$k]->{"DAY13"}, $visits_stud[$k]->{"DAY14"}, $visits_stud[$k]->{"DAY15"}, $visits_stud[$k]->{"DAY16"}, $visits_stud[$k]->{"DAY17"}, $visits_stud[$k]->{"DAY18"}, $visits_stud[$k]->{"DAY19"}, $visits_stud[$k]->{"DAY20"}, $visits_stud[$k]->{"DAY21"}, $visits_stud[$k]->{"DAY22"}, $visits_stud[$k]->{"DAY23"}, $visits_stud[$k]->{"DAY24"}, $visits_stud[$k]->{"DAY25"}, $visits_stud[$k]->{"DAY26"}, $visits_stud[$k]->{"DAY27"}, $visits_stud[$k]->{"DAY28"}, $visits_stud[$k]->{"DAY29"}, $visits_stud[$k]->{"DAY30"}, $visits_stud[$k]->{"DAY31"}, $visits_stud[$k]->{"NOTES"}, $us_id);
                   }
                   ################################################################################################
                }
                
                #############�� ������ �������� �������� �������� ��� ��� ���� � ��
                #���������� ID ������ ��������, ����� ������� ��� ���� � ��
                $sql="select GROUP_ID from groups_students where PUPILS_NUM_DOGOVOR=?";
                $sth=$dbh->prepare($sql);
                $sth->execute($data[$u]);
                my @group_id = $sth->fetchrow_array;
                ################################################
  
                $sql="select PERIOD, DATE_LESSON, TOPIC, HOME_WORK from topic_homework where GROUP_ID=?";
                $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                $sth->execute($group_id[0]);
                while ($data=$sth->fetchrow_hashref) {
                push @homework_stud, $data;
                }
 
                if (@homework_stud)
                {
                   #����� ������ �� ������� ��������� ������� �� � ��������� �� � �����
                   for (my $s=0; $s<=$#homework_stud; $s++)
                   {
                      $sql="insert into topic_homework_archive (PUPILS_NUM_DOGOVOR, PERIOD, DATE_LESSON, TOPIC, HOME_WORK, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,NOW())";
                      $sth=$dbh->prepare($sql);
                      $sth->execute($data[$u], $homework_stud[$s]->{"PERIOD"}, $homework_stud[$s]->{"DATE_LESSON"}, $homework_stud[$s]->{"TOPIC"}, $homework_stud[$s]->{"HOME_WORK"}, $us_id);
                   }
                   ################################################################################################
                } 
                
                #############�� ������ �������� �������� �������� ��� ��� ������
                $sql="select topic_homework.TOPIC, feedback_lessons.PUPILS_NUM_DOGOVOR, feedback_lessons.TEXT_FEEDBACK from topic_homework, feedback_lessons where topic_homework.ID=feedback_lessons.ID_TOPIC_HOMEWORK and feedback_lessons.PUPILS_NUM_DOGOVOR=?";
                $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                $sth->execute($data[$u]);
                while ($data=$sth->fetchrow_hashref) {
                push @feedback_stud, $data;
                }
 
                if (@feedback_stud)
                {
                   #����� ������ �� ������� ��������� ������� ��������� � ��������� �� � �����
                   for (my $t=0; $t<=$#feedback_stud; $t++)
                   {
                      $sql="insert into feedback_lessons_archive (PUPILS_NUM_DOGOVOR, TOPIC, TEXT_FEEDBACK, DATETIME_CREATE) values (?,?,?,NOW())";
                      $sth=$dbh->prepare($sql);
                      $sth->execute($feedback_stud[$t]->{"PUPILS_NUM_DOGOVOR"}, $feedback_stud[$t]->{"TOPIC"}, $feedback_stud[$t]->{"TEXT_FEEDBACK"});
                   }
                   ################################################################################################
                }
                
                #���������� �������� �� � ������ �� ������� ����������� ������ ������ ��������, ����� �������� ��� �������� ��������� ������ ���. ���� ��������, �� ������� ������ � �� �� ������� ������, �.�. ��� ����� ��� ������ ����������� ���������. ���� �� �� �������� � ������� ������� ���������, �� ������ ����� �������.
                $sql="select pupils_num_dogovor from groups_students where group_id=? and pupils_num_dogovor not like ?";
                $sth=$dbh->prepare($sql);
                $sth->execute($group_id[0], $data[$u]);
                my @exist_stud = $sth->fetchrow_array;
                ################################################
                
				
				#############�� ������ �������� �������� �������� ��� ���������� ������� �������� �� �������� � �����
                $sql="select PUPILS_NUM_DOGOVOR, PERIOD, UUID from past_academ_years where PUPILS_NUM_DOGOVOR=?";  
                $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                $sth->execute($data[$u]);
                while ($data=$sth->fetchrow_hashref) {
                push @past_academ_years, $data;
                }
 
                if (@past_academ_years)
                { 
                   #����� ������ �� ������� ��������� �������� �������� � ��������� �� � �����, � ����� ��������� ������ �� ������ ������ ������� ������ ��������
                   for (my $v=0; $v<=$#past_academ_years; $v++)
                   {
                      $sql="insert into past_academ_years_archive (PUPILS_NUM_DOGOVOR, PERIOD, UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,NOW())";
                      $sth=$dbh->prepare($sql);
                      $sth->execute($past_academ_years[$v]->{"PUPILS_NUM_DOGOVOR"}, $past_academ_years[$v]->{"PERIOD"}, $past_academ_years[$v]->{"UUID"}, $us_id);
           
           
                      ##����� �� ��������� �������� � ����������� � ������� ������ ��������, �������� �� �� UUID � ���������
                      #############�� UUID �������� ������ �� ���������� ��������
                      $sql="select TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, PAST_ACADEM_YEARS_UUID from past_academ_years_documents where PAST_ACADEM_YEARS_UUID=?";  
                      $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                      $sth->execute($past_academ_years[$v]->{"UUID"});
                      while ($data=$sth->fetchrow_hashref) {
                      push @past_academ_years_documents, $data;
                      } 
  
                     if (@past_academ_years_documents)
                     { 
                        #����� ������ �� ������� ��������� ������� � �������, ���� ������ � �������� ����� ���� ������ ����! �������, �� ����, ����� ���� �� �����.
                        for (my $v1=0; $v1<=$#past_academ_years_documents; $v1++)
                        {
                           $sql="insert into past_academ_years_documents_archive (TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_documents[$v1]->{"TYPE_DOC"}, $past_academ_years_documents[$v1]->{"COURSE"}, $past_academ_years_documents[$v1]->{"TYPE_GROUP"}, $past_academ_years_documents[$v1]->{"PRICE_COURSE"}, $past_academ_years_documents[$v1]->{"DATE_START_DOGOVOR"}, $past_academ_years_documents[$v1]->{"DATE_END_DOGOVOR"}, $past_academ_years_documents[$v1]->{"TEXT_DOCUM"}, $past_academ_years_documents[$v1]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }        
           
                     #############�� UUID �������� ������ �� ������
                     $sql="select GROUP_NAME, LANGUAGE, PROGRAMM_NAME, TEACHER_FIO, BRANCH, PAST_ACADEM_YEARS_UUID from past_academ_years_group_data where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_groups, $data;
                     } 
 
                     if (@past_academ_years_groups)
                     { 
                        #����� ������ �� ������� ��������� ������� � ������� � ��������� �� � �����
                        for (my $v2=0; $v2<=$#past_academ_years_groups; $v2++)
                        {
                           $sql="insert into past_academ_years_group_data_archive (GROUP_NAME, LANGUAGE, PROGRAMM_NAME, TEACHER_FIO, BRANCH, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_groups[$v2]->{"GROUP_NAME"}, $past_academ_years_groups[$v2]->{"LANGUAGE"}, $past_academ_years_groups[$v2]->{"PROGRAMM_NAME"}, $past_academ_years_groups[$v2]->{"TEACHER_FIO"}, $past_academ_years_groups[$v2]->{"BRANCH"}, $past_academ_years_groups[$v2]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }
           
                     #############�� UUID �������� ������ �� �������
                     $sql="select NUM_ORDER, TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, PAST_ACADEM_YEARS_UUID, USER_CREATED_ORDER,STATUS from past_academ_years_orders where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_orders, $data;
                     } 
 
                     if (@past_academ_years_orders)
                     { 
                        #����� ������ �� ������� ��������� ������� � �������, � ��������� �� � �����
                        for (my $v3=0; $v3<=$#past_academ_years_orders; $v3++)
                        {
                           $sql="insert into past_academ_years_orders_archive (NUM_ORDER, TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, PAST_ACADEM_YEARS_UUID, USER_CREATED_ORDER, USER_ID, DATETIME_CREATE, STATUS) values (?,?,?,?,?,?,?,?,?,NOW(),?)";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_orders[$v3]->{"NUM_ORDER"}, $past_academ_years_orders[$v3]->{"TYPE_DOC"}, $past_academ_years_orders[$v3]->{"DATE_PAY"}, $past_academ_years_orders[$v3]->{"PUPILS_NUM_DOGOVOR_OR_KA"}, $past_academ_years_orders[$v3]->{"OSNOVANIE"}, $past_academ_years_orders[$v3]->{"SUMM_OPL"}, $past_academ_years_orders[$v3]->{"PAST_ACADEM_YEARS_UUID"}, $past_academ_years_orders[$v3]->{"USER_CREATED_ORDER"}, $us_id, $past_academ_years_orders[$v3]->{"STATUS"});
                        }
                        ################################################################################################
                     }           
           
                     #############�� UUID �������� ������ �� �������
                     $sql="select PERIOD, SUMM_4_OPL, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES, PAST_ACADEM_YEARS_UUID from past_academ_years_pays where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_pays, $data;
                     } 
 
                     if (@past_academ_years_pays)
                     { 
                        #����� ������ �� ������� ��������� ������� �� ������� � ��������� �� � �����
                        for (my $v4=0; $v4<=$#past_academ_years_pays; $v4++)
                        {
                           $sql="insert into past_academ_years_pays_archive (PERIOD, SUMM_4_OPL, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_pays[$v4]->{"PERIOD"}, $past_academ_years_pays[$v4]->{"SUMM_4_OPL"}, $past_academ_years_pays[$v4]->{"OPL_SUMM"}, $past_academ_years_pays[$v4]->{"DATE_OF_PAY"}, $past_academ_years_pays[$v4]->{"STATUS"}, $past_academ_years_pays[$v4]->{"NOTES"}, $past_academ_years_pays[$v4]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }
					 
					 #############�� UUID �������� ������ �� ����������
                     $sql="select PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES, PAST_ACADEM_YEARS_UUID from past_academ_years_visits where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_visits, $data;
                     } 
 
                     if (@past_academ_years_visits)
                     { 
                        #����� ������ �� ������� ��������� ������� � ����������
                        for (my $v5=0; $v5<=$#past_academ_years_visits; $v5++)
                        {
                           $sql="insert into past_academ_years_visits_archive (PERIOD, DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7, DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14, DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21, DAY22, DAY23, DAY24, DAY25, DAY26, DAY27, DAY28, DAY29, DAY30, DAY31, NOTES, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_visits[$v5]->{"PERIOD"}, $past_academ_years_visits[$v5]->{"DAY1"}, $past_academ_years_visits[$v5]->{"DAY2"}, $past_academ_years_visits[$v5]->{"DAY3"}, $past_academ_years_visits[$v5]->{"DAY4"}, $past_academ_years_visits[$v5]->{"DAY5"}, $past_academ_years_visits[$v5]->{"DAY6"}, $past_academ_years_visits[$v5]->{"DAY7"}, $past_academ_years_visits[$v5]->{"DAY8"}, $past_academ_years_visits[$v5]->{"DAY9"}, $past_academ_years_visits[$v5]->{"DAY10"}, $past_academ_years_visits[$v5]->{"DAY11"}, $past_academ_years_visits[$v5]->{"DAY12"}, $past_academ_years_visits[$v5]->{"DAY13"}, $past_academ_years_visits[$v5]->{"DAY14"}, $past_academ_years_visits[$v5]->{"DAY15"}, $past_academ_years_visits[$v5]->{"DAY16"}, $past_academ_years_visits[$v5]->{"DAY17"}, $past_academ_years_visits[$v5]->{"DAY18"}, $past_academ_years_visits[$v5]->{"DAY19"}, $past_academ_years_visits[$v5]->{"DAY20"}, $past_academ_years_visits[$v5]->{"DAY21"}, $past_academ_years_visits[$v5]->{"DAY22"}, $past_academ_years_visits[$v5]->{"DAY23"}, $past_academ_years_visits[$v5]->{"DAY24"}, $past_academ_years_visits[$v5]->{"DAY25"}, $past_academ_years_visits[$v5]->{"DAY26"}, $past_academ_years_visits[$v5]->{"DAY27"}, $past_academ_years_visits[$v5]->{"DAY28"}, $past_academ_years_visits[$v5]->{"DAY29"}, $past_academ_years_visits[$v5]->{"DAY30"}, $past_academ_years_visits[$v5]->{"DAY31"}, $past_academ_years_visits[$v5]->{"NOTES"}, $past_academ_years_visits[$v5]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }
                     
                     #############�� UUID �������� ������ �� ��
                     $sql="select PERIOD, DATE_LESSON, TOPIC, HOME_WORK, PAST_ACADEM_YEARS_UUID from past_academ_years_topic_homework where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_homework, $data;
                     } 
 
                     if (@past_academ_years_homework)
                     { 
                        #����� ������ �� ������� ��������� ������� � ����������
                        for (my $v6=0; $v6<=$#past_academ_years_homework; $v6++)
                        {
                           $sql="insert into past_academ_years_topic_homework_archive (PERIOD, DATE_LESSON, TOPIC, HOME_WORK, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_homework[$v6]->{"PERIOD"}, $past_academ_years_homework[$v6]->{"DATE_LESSON"}, $past_academ_years_homework[$v6]->{"TOPIC"}, $past_academ_years_homework[$v6]->{"HOME_WORK"}, $past_academ_years_homework[$v6]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }
                     
                     #############�� UUID �������� ������ �� ������ ��������
                     $sql="select TOPIC, TEXT_FEEDBACK, PAST_ACADEM_YEARS_UUID from past_academ_years_feedback_lessons where PAST_ACADEM_YEARS_UUID=?";  
                     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                     $sth->execute($past_academ_years[$v]->{"UUID"});
                     while ($data=$sth->fetchrow_hashref) {
                     push @past_academ_years_feedback, $data;
                     } 
 
                     if (@past_academ_years_feedback)
                     { 
                        #����� ������ �� ������� ��������� ������� � ����������
                        for (my $v7=0; $v7<=$#past_academ_years_feedback; $v7++)
                        {
                           $sql="insert into past_academ_years_feedback_lessons_archive (TOPIC, TEXT_FEEDBACK, PAST_ACADEM_YEARS_UUID, USER_ID, DATETIME_CREATE) values (?,?,?,?, NOW())";
                           $sth=$dbh->prepare($sql);
                           $sth->execute($past_academ_years_feedback[$v7]->{"TOPIC"}, $past_academ_years_feedback[$v7]->{"TEXT_FEEDBACK"}, $past_academ_years_feedback[$v7]->{"PAST_ACADEM_YEARS_UUID"}, $us_id);
                        }
                        ################################################################################################
                     }
           
                     #�������� ���������� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_documents where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});
  
                     #�������� ������ � ������� � �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_group_data where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});
  
                     #�������� ������� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_orders where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});
  
                     #�������� ����� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_pays where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});  
					 
					 #�������� ��������� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_visits where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});  
           
                     #�������� �� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_topic_homework where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});  
           
                     #�������� ������� �������� �� ������� ������ �����
                     $sql="delete from past_academ_years_feedback_lessons where PAST_ACADEM_YEARS_UUID=?";
                     $sth=$dbh->prepare($sql);
                     $sth->execute($past_academ_years[$v]->{"UUID"});
           
                     #������� �������
                     @past_academ_years_documents=();
                     @past_academ_years_groups=();
                     @past_academ_years_orders=();
                     @past_academ_years_pays=();
					 @past_academ_years_visits=();
                     @past_academ_years_homework=();
                     @past_academ_years_feedback=();
                  }   
                  ################################################################################################
                } 
  
                #############�� ������ �������� �������� �������� �� pupils ��� ��� �������� � �����
                $sql="select pupils.Num_dogovor, pupils.FIO, pupils.DATE_OF_BORN, pupils.PLACE_OF_WORK, pupils.POSITION_FACULT, pupils.HOME_ADDRESS, pupils.MOBILE_PHONE, pupils.HOME_PHONE, pupils.WORK_PHONE, pupils.EMAIL, pupils.PASSPORT, source_about_us.SOURCE, pupils.DATE_OF_FILLING, pupils.FIO_PARENT, pupils.NUM_PASSPORT_PARENT, pupils.SER_PASSPORT_PARENT, pupils.KEM_VIDANO_PASSPORT_PARENT, pupils.KOGDA_VIDANO_PASSPORT_PARENT, pupils.PASSPORT_NUM, pupils.PASSPORT_VIDAN, pupils.PASSPORT_DATE, pupils.SEX, branches.BRANCH, pupils.USER_ID, pupils.MOBILE_CHILD, pupils.GROUP_ID, pupils.GUID, pupils.MARK_FROM_ZAYAV, pupils.STUDENT_INTERESTS, pupils.AGREMMENT_GET_SMS, pupils.AGREMMENT_GET_EMAIL, pupils.AGREMMENT_USE_PHOTO, pupils.KIND_PROG_FROM_DOGOVOR from pupils, branches, source_about_us where pupils.BRANCH=branches.ID and pupils.SOURCE_ABOUT_US=source_about_us.ID and Num_dogovor=?";  
                $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
                $sth->execute($data[$u]);
                my @row_pupil = $sth->fetchrow_array;  
 
                if (@row_pupil)
                {
                   $sql="insert into pupils_archive (Num_dogovor, FIO, DATE_OF_BORN, PLACE_OF_WORK, POSITION_FACULT, HOME_ADDRESS, MOBILE_PHONE, HOME_PHONE, WORK_PHONE, EMAIL, PASSPORT, SOURCE_ABOUT_US, DATE_OF_FILLING, FIO_PARENT, NUM_PASSPORT_PARENT, SER_PASSPORT_PARENT, KEM_VIDANO_PASSPORT_PARENT, KOGDA_VIDANO_PASSPORT_PARENT, PASSPORT_NUM, PASSPORT_VIDAN, PASSPORT_DATE, SEX, BRANCH, USER_ID, MOBILE_CHILD, GROUP_ID, GUID, MARK_FROM_ZAYAV, STUDENT_INTERESTS, AGREMMENT_GET_SMS, AGREMMENT_GET_EMAIL, AGREMMENT_USE_PHOTO, KIND_PROG_FROM_DOGOVOR) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
                   $sth=$dbh->prepare($sql);
                   $sth->execute($row_pupil[0], $row_pupil[1], $row_pupil[2], $row_pupil[3], $row_pupil[4], $row_pupil[5], $row_pupil[6], $row_pupil[7], $row_pupil[8], $row_pupil[9], $row_pupil[10], $row_pupil[11], $row_pupil[12], $row_pupil[13], $row_pupil[14], $row_pupil[15], $row_pupil[16], $row_pupil[17], $row_pupil[18], $row_pupil[19], $row_pupil[20], $row_pupil[21], $row_pupil[22], $us_id, $row_pupil[24], $row_pupil[25], $row_pupil[26], $row_pupil[27], $row_pupil[28], $row_pupil[29], $row_pupil[30], $row_pupil[31], $row_pupil[32]);
                   ################################################################################################
                 }
     

                 #�������� �������� ��������
                 $sql="delete from pays where pupils_num_dogovor=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� ���������� ��������
                 $sql="delete from document_students where PUPILS_Num_dogovor=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� ������� ��������� �������� (���������� �������)
                 $sql="delete from calendar_pupils where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� ������� �� ������� ��������
                 $sql="delete from history_students where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� �������� �������� �� ������
                 $sql="delete from groups_students where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
				 
				  #�������� ����������� ��������
                 $sql="delete from events_pupils where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� ������������ ����� ��������
                 $sql="delete from pays_without_group where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
    
                 #�������� ������� ������ ������� ������ ������ � ��������
                 $sql="delete from past_academ_years where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
				 
				 #�������� ��������� ��������
                 $sql="delete from visits where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� �� ��������
                 if (!@exist_stud)
                 {    
                    $sql="delete from topic_homework where GROUP_ID=?";
                    $sth=$dbh->prepare($sql);
                    $sth->execute($group_id[0]);
                 }
  
                 #�������� ������� ��������
                 $sql="delete from feedback_lessons where PUPILS_NUM_DOGOVOR=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
  
                 #�������� ������ �������� �� ������� Pupils
                 $sql="delete from pupils where Num_dogovor=?";
                 $sth=$dbh->prepare($sql);
                 $sth->execute($data[$u]);
                 
               
                 $dbh->commit; #���������� ����������
                 $dbh->{AutoCommit}=1; 
                 $dbh->{RaiseError}=0;  

                  @pays=();
                  @doc_students=();
                  @calend_pupils=();
				  @events_pupils=();
                  @history_stud=();
				  @opl_without_gr=();
                  @past_academ_years=();
                  @group_stud=();
                  @row_pupil=(); 
				  @visits_stud=();
                  @homework_stud=();
                  @feedback_stud=();
                  @group_id=();
             
              };
  if ($@) # ���� ��������� ������, �� ���������� ����������
  {
  # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
  eval { $dbh->rollback; };
  }
  
  } 
  
  $dbh->disconnect; 
  ################################################

  my $ans="������� ���������� ������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################

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
