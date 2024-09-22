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
my $able_move_students_between_groups=$sess->param('able_move_students_between_groups');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

  if ($able_move_students_between_groups==1) #������� ����� �� ���������� ������������ ����������� ����������� ����� �������� ���������. ��������� ��� �� ���������� ����������� �� ������.
  {  
     my @data=param('dat');

     if (scalar(@data)!=2)
     {
        my $ans="�� ��������� �������� ������!";
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

     foreach my $check (@data)
     {
        if ($check!~m/^\d+$/g)
        {
          my $ans="�� ��������� �������� ��������������!";
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});
          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          exit;
        }
        
     }


     ##############################����������, ������� �� � ������, � ������� ��������� ��������, �������. ���� ���, �� ���������� ������!
     my $dbh0=ConnectDB->connect;
     my $sth0=$dbh0->do("SET NAMES 'cp1251'");
     my $sql0="select GROUP_ID from lessons where GROUP_ID=?";
     $sth0=$dbh0->prepare($sql0); #��� �������� ������� �� ���������� ��������
     $sth0->execute($data[1]);
     my @lessons = $sth0->fetchrow_array; 
  
     if (!@lessons)
     {
        my $ans="����������� �������� � ��������� ������ ����������, �.�. � ������ �� ������� �������"; 
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
  
     ##############################���������� ������������ � ������ ���������� ������� ������
     my $dbh1=ConnectDB->connect;
     my $sth1=$dbh1->do("SET NAMES 'cp1251'");
     my $sql1="select kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.GROUP_NAME, groups.START_DATE, groups.END_DATE, groups.COURSE_PRICE from groups, groups_students, kind_languages, kind_programm where kind_languages.ID=groups.LANGUAGE and kind_programm.ID=groups.KIND_PROGRAMM and groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
     $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
     $sth1->execute($data[0]);
     my @param_gr = $sth1->fetchrow_array; 
  
     if (!@param_gr)
     {
        my $ans="����������� �������� � ��������� ������ ����������, �.�. ������� ������ �� �������� � �����-���� ������. � ������ ������ � ����������� ��� �������������, �.�. ������� �������� ����� ����� ��������� � ������ ������"; 
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
 
 
     ################################### �� ������ �������� � �������� �������� ID ������ �� ���������, ����� ������� ������������ ������� �������� �� ������ � ������.
  
     #���������� ����� ���������� � ���� Eval � ���������� $@, ���� ��������� ������ �� ����� ���������� SQL ������ � ����� Eval, �� ��������� ����� ��������
     my $dbh=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
     my $sth=$dbh->do("SET NAMES 'cp1251'");
     eval {  

     #############���������� ��������� ������ � ������� calendar_pupils
     my $sql="update calendar_pupils set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[1], $data[0]);
  
  
     #############���������� ��������� ������ � ������� pays
     $sql="update pays set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[1], $data[0]);
  
  
     #############���������� ��������� ������ � ������� groups_students
     $sql="update groups_students set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[1], $data[0]);

    #############?????????? ????????? ????????? ??????? ? ??????? visits
    $sql="update visits set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
    $sth=$dbh->prepare($sql); #??? ???????? ??????? ?? ?????????? ????????
    $sth->execute($data[1], $data[0]);
 
     #############��������� ������ � �������� � ������� ��������
     $sql="insert into history_students (PUPILS_NUM_DOGOVOR, TEXT, DATETIME_CREATE, USER_ID) values (?,?,NOW(),?)";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[0], '������� �� ������: '.$param_gr[2].' (����: '.$param_gr[0].', ���������: '.$param_gr[1].', ���� �����: '.$param_gr[5].', ������ �������� ������: � '.$param_gr[3].' �� '.$param_gr[4].')', $us_id);
 
     #############� ���� IS_MOVED ��������� 1, ��� ��������� �� ��, ��� ������� ��� ��������� ����� ��������
     $sql="update pupils set IS_MOVED=1 where Num_dogovor=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[0]);
 
     #############������� ������������ ������ �� ��������� �������� (���������� �������), ��� ������� ���������� �� ������ � ������� ��������� �������
     $sql="delete from calendar_pupils where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[0]);
  
     #������� ������ � �������� ����������� � ������, ���� ��������� ��������, ����� ������� ��� ����������
     $sql="select UUID, TEACHER_ID, ALL_LESSONS from lessons where GROUP_ID=?";
     $sth=$dbh->prepare($sql); #��� �������� ������� �� ���������� ��������
     $sth->execute($data[1]);  
     my @row_data = $sth->fetchrow_array;
  
     #�������� ��� ������� ��� ������� ��� � �������� ������� � ���������� ��������
     $sql="select FIO from teachers where ID=?";
     $sth=$dbh->prepare($sql);
     $sth->execute($row_data[1]);
     #� ������ ���������� ����������� ������
     my @row_teacher = $sth->fetchrow_array;
     ################################################ 
 
     #��������������� ������ ���������� �� DAYS_OF_LESSONS � ������
     my @full_day_time_data=split(",", $row_data[2]);
    
     #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
     for (my $t9=0; $t9<=$#full_day_time_data; $t9=$t9+3)
     {  
        $sql="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
        $sth=$dbh->prepare($sql);
        $sth->execute($full_day_time_data[$t9]." ".$full_day_time_data[$t9+1], $full_day_time_data[$t9]." ".$full_day_time_data[$t9+2], "�������. �������������:  ".$row_teacher[0], $data[0], $data[1], $row_data[0], $us_id);
     }
 
  
     $dbh->commit; #���������� ����������
     $dbh->{AutoCommit}=1; 
     $dbh->{RaiseError}=0;
     };
     if ($@) # ���� ��������� ������, �� ���������� ����������
     {
       # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
     eval { $dbh->rollback; };
     }
     $dbh->disconnect; 
     ################################################


     my $ans="����������� ��������� ������!";
     #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
     my $ans="�� �� ������ ����� ���������� ���������!";
     #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
     my $res=$ans;

     #convert  data to JSON
     my $op = JSON -> new -> pretty(1);
     my $json = $op -> encode({result => $res});

     print $cgi->header('application/json;charset=windows-1251');
     print $json;
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
