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
my $able_send_sms=$sess->param('able_send_sms');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        
if ($able_send_sms==1) #������� ����� �� ���������� ������������ ���������� ���. ��������� ��� �� ���������� ����������� �� ������.
{ 
   
   #�������� ����� � ������ �� ��� ����� � ��
   my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth4=$dbh4->do("SET NAMES 'cp1251'");
   my $sql4="select LOGIN, PASSW from sms_gate";
   $sth4=$dbh4->prepare($sql4);
   $sth4->execute();
   #� ������ ���������� ����������� ������
   my @row_data = $sth4->fetchrow_array;
   
   if (!@row_data)
   {
      my $ans="�� ������ ��������� ��� - �����. ������� ��� ����� � ������� \"���-����\" ���� <a href=\"administration_tools.cgi?SID=$SID\">\"����������-���������\"</a>";
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      exit;
   }
   
   my @data=param('data');
   my $text_sms=param('text_sms');
   $text_sms=~s/\0//g; $text_sms=~s/\.\.//g; $text_sms=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

   if (length($text_sms)==0)
   {
      my $ans="�� ������ ����� ��� ��������!";
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      exit;
   }  

   if (scalar(@data)==0)
   {
      my $ans="�� ������� ������������� ��� �������� ���!";
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
        $ch=~s/\D//gs; #������� �� ������ �������� ����� ������� ����� ����.                
        
        #�������� �� ������ ������
        if (length($ch)!=11)
        {
            my$ans="�������� ��������! ���� ��� ����� ������� ����� ������������ ������. ������ ������ ������ ���� 11 �������� (������ � ����� ������ 7). ������: 79095556677";
            #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        ###########
        
        #�������� �� ������ ����� 7 � ������ ��������
        if (substr($ch,0,1)!=7)
        {
            my$ans="�������� ��������! ���� ��� ����� ������� ����� ������ ����� �������� �� 7. ��� ������ ������ ���������� � ����� 7 (������������� ��� ������).";
            #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        ###########
   }

   my $login = $row_data[0];
   my $password = $row_data[1];

   #�������� XML �������� ��� �������� ��� ��������
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
    <text>'.$text_sms.'</text>   
    </message>    
    <numbers>'; 
    
   my $second_part = '</numbers>
                      </SMS>';

   my @numbers;
   #��������� ������ �������� ��� �������� � ������ <numbers>
   foreach my $number (@data)
   {
      push (@numbers, "<number>".$number."</number>");
   }
   #����������� ����������� ������ � ������ ��� ������� ��� � XML ���������
   my $middle_part = join("", @numbers);

   #������ ������������� XML ��������� � �������� ��� ��������
   my $ready_XML=$first_part.$middle_part.$second_part;

   #���������� ��� ����� �� ���
   my $ua = new LWP::UserAgent;

   my $response = $ua->post('http://api.myatompark.com/members/sms/xml.php',{ XML => $ready_XML});


   my$ans="�������� ��������� ������!";
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
else
{
        my $ans="�� �� ������ ����� ���������� ���!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
