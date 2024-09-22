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

######������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass))
{

my $curr_psw=$cgi->param('curr_psw');
my $new_psw=$cgi->param('new_psw');
my $new_psw1=$cgi->param('new_psw1');

$curr_psw=~s/\0//g; $curr_psw=~s/\.\.//g; $curr_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw=~s/\0//g; $new_psw=~s/\.\.//g; $new_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw1=~s/\0//g; $new_psw1=~s/\.\.//g; $new_psw1=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#������� ������
$curr_psw=md5_hex($curr_psw);

#�������� �� ������������� ������������ � �� �� ���������� ������ � ������
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select * from usr where LOGIN like ? and PASSW like ?";
$sth=$dbh->prepare($sql);
$sth->execute($formLogin,$curr_psw);

#�������� ���-�� �����
my $rows_affected = $sth->rows();

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

$dbh->disconnect;

#########���� ������� ����� 0, �� ������ ��� ����� ���� �� �������
if ($rows_affected==0)
{
    my $ans="������� ������ ����� �� �����!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit();
}
###################################################################


#######���� ����� ������ �� ���������, ���������� ������������.
if ($new_psw ne $new_psw1)
{
  my $ans="��������� ������ �� ���������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

#######���� ����� ������ ��������� � ����������, �� ���������� ������������ � ��������� ���������.
if ((md5_hex($new_psw) eq $curr_psw) && (md5_hex($new_psw1) eq $curr_psw))
{
  my $ans="��������� ������ ��������� � ����������. ��������� ����������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################


######���� ������ �� �������� ������� ���������, �� ������� ��������� ������������
if (($new_psw!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm) && ($new_psw1!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm))
{
  my $ans="��������� ������ �� ������������� ����������� ���������! ������ ������ ����� ������ �� 8 �� 20 ��������, ��������� ���� �� ���� �����, ���� ����� ��������� � ���������, � ����� ��������� ���� �� �������� (@#\$%!).";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################


###########��������� ��������� �� ��������� ������ � ������� � ������� ����������� ����� �������, � ���� ���������, �� ������ UPDATE ������
if ($row[1] eq $formLogin && $row[2] eq $curr_psw)
{
  #�������� ���-�� ������ �������. ���� ������� ����� 5, �� ��������� ������ ������ � ������� old_passw, ���� ������ 5, �� ������ update �� ������ ������� � ���������� ����� ��������
  my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="select USER_ID from old_passw where USER_ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row[0]);
  #�������� ���-�� �����
  my $rows_count = $sth2->rows();
  
  if ($rows_count<5) 
  {
     #�������� ��������� ������������� ������. ���� ������ ���� ����� ��������� 5-�� ��������, �� ��� ���� ��������!
     my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
     my $sth2=$dbh2->do("SET NAMES 'cp1251'");
     my $sql2="select PASSW from old_passw where USER_ID=? and PASSW=?";
     $sth2=$dbh2->prepare($sql2);
     $sth2->execute($row[0], md5_hex($new_psw));
     #� ������ ���������� ����������� ������
     my @row_psw = $sth2->fetchrow_array;
     
     if (@row_psw)
     {
             my $ans="�������� ������ ������������ � ������ 5 ���������� �������. ������� ������ ������!";
             #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
     else
     {     
             
             #��������� � ������� old_passw ������� ������, ����� ������� ��� �� �����
             my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
             my $sth3=$dbh3->do("SET NAMES 'cp1251'");
             my $sql3="insert into old_passw (USER_ID, PASSW, DATETIME_CREATE) values (?,?, NOW())";
             $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
             $sth3->execute($row[0], $curr_psw);
             $dbh3->disconnect;
             
             #������ ������
             my $md5_psw=md5_hex($new_psw); # ������� ������
             my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
             my $sth1=$dbh1->do("SET NAMES 'cp1251'");
             my $sql1="update usr set PASSW=?, PASSW_DATE_EXPIRED=ADDDATE(NOW(), ?) where ID like ?";
             $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
             $sth1->execute($md5_psw, $row[63], $row[0]);
             $dbh1->disconnect;

             my $ans="������ ������� �������!";
             #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
  }
  
  
  if ($rows_count==5)
  {
     #�������� ��������� ������������� ������. ���� ������ ���� ����� ��������� 5-�� ��������, �� ��� ���� ��������!
     my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
     my $sth2=$dbh2->do("SET NAMES 'cp1251'");
     my $sql2="select PASSW from old_passw where USER_ID=? and PASSW=?";
     $sth2=$dbh2->prepare($sql2);
     $sth2->execute($row[0], md5_hex($new_psw));
     #� ������ ���������� ����������� ������
     my @row_psw = $sth2->fetchrow_array;
     
     if (@row_psw)
     {
             my $ans="�������� ������ ������������ � ������ 5 ���������� �������. ������� ������ ������!";
             #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
     else
     {     
             #����������� �������� ������ ������ � ������ ������� ��������, ��� �� update
             my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
             my $sth4=$dbh4->do("SET NAMES 'cp1251'");
             my $sql4="select min(DATETIME_CREATE) as dt_cr from old_passw where USER_ID=?";
             $sth4=$dbh4->prepare($sql4);
             $sth4->execute($row[0]);
             #� ������ ���������� ����������� ������
             my @row_old_psw = $sth4->fetchrow_array;
            
            
             #Update � ������� old_passw ������ � ������� � ���������� �����
             my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
             my $sth3=$dbh3->do("SET NAMES 'cp1251'");
             my $sql3="update old_passw set PASSW=?, DATETIME_CREATE=NOW() where USER_ID=? and DATETIME_CREATE=?";
             $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
             $sth3->execute($curr_psw, $row[0], $row_old_psw[0]);
             $dbh3->disconnect;
             
             #������ ������
             my $md5_psw=md5_hex($new_psw); # ������� ������
             my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
             my $sth1=$dbh1->do("SET NAMES 'cp1251'");
             my $sql1="update usr set PASSW=?, PASSW_DATE_EXPIRED=ADDDATE(NOW(), ?) where ID like ?";
             $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
             $sth1->execute($md5_psw, $row[63], $row[0]);
             $dbh1->disconnect;

             my $ans="������ ������� �������!";
             #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
  }

}
##############################################################

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



