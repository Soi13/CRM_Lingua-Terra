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

###############��������� ������� ���� � �� ����� ��������� �������. ��� ����� ������������ ���� DATA_CHILD. ��� ���������� ��� ������� ��������.
my $query=CGI->new;
my @DATA_CHILD = $query->param('DATA_CHILD');

for(my $n=0; $n<=$#DATA_CHILD; $n++ )
{
        $DATA_CHILD[$n]=~s/\0//g;
        $DATA_CHILD[$n]=~s/\.\.//g;
        $DATA_CHILD[$n]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($DATA_CHILD[$n],'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
}
####################


################��������� ��������� �����
my $FIO=param('FIO');
my $POSITION=param('POSITION');
my $PHONE=param('PHONE');
my $EMAIL=param('EMAIL');
my $DATE_OF_BORN=param('DATE_OF_BORN');
my $SER_PASSPORT=param('SER_PASSPORT');
my $NUM_PASSPORT=param('NUM_PASSPORT');
my $KEM_VIDAN=param('KEM_VIDAN');
my $KOGDA_VIDAN=param('KOGDA_VIDAN');
my $KOD_PODRAZDELEN=param('KOD_PODRAZDELEN');
my $INN=param('INN');
my $SNILS=param('SNILS');
my $HOME_ADDRESS=param('HOME_ADDRESS');
my $DATE_WORK_DOGOVOR=param('DATE_WORK_DOGOVOR');
my $AGREMMENT_GET_EMAIL=param('AGREMMENT_GET_EMAIL');

$FIO=~s/\0//g; $FIO=~s/\.\.//g; $FIO=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$POSITION=~s/\0//g; $POSITION=~s/\.\.//g; $POSITION=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PHONE=~s/\0//g; $PHONE=~s/\.\.//g; $PHONE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$EMAIL=~s/\0//g; $EMAIL=~s/\.\.//g; $EMAIL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_OF_BORN=~s/\0//g; $DATE_OF_BORN=~s/\.\.//g; $DATE_OF_BORN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SER_PASSPORT=~s/\0//g; $SER_PASSPORT=~s/\.\.//g; $SER_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$NUM_PASSPORT=~s/\0//g; $NUM_PASSPORT=~s/\.\.//g; $NUM_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KEM_VIDAN=~s/\0//g; $KEM_VIDAN=~s/\.\.//g; $KEM_VIDAN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOGDA_VIDAN=~s/\0//g; $KOGDA_VIDAN=~s/\.\.//g; $KOGDA_VIDAN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOD_PODRAZDELEN=~s/\0//g; $KOD_PODRAZDELEN=~s/\.\.//g; $KOD_PODRAZDELEN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$INN=~s/\0//g; $INN=~s/\.\.//g; $INN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SNILS=~s/\0//g; $SNILS=~s/\.\.//g; $SNILS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$HOME_ADDRESS=~s/\0//g; $HOME_ADDRESS=~s/\.\.//g; $HOME_ADDRESS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_WORK_DOGOVOR=~s/\0//g; $DATE_WORK_DOGOVOR=~s/\.\.//g; $DATE_WORK_DOGOVOR=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$AGREMMENT_GET_EMAIL=~s/\0//g; $AGREMMENT_GET_EMAIL=~s/\.\.//g; $AGREMMENT_GET_EMAIL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($FIO,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($POSITION,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($PHONE,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($EMAIL,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($DATE_OF_BORN,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($SER_PASSPORT,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($NUM_PASSPORT,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($KEM_VIDAN,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($KOGDA_VIDAN,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($KOD_PODRAZDELEN,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($INN,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($SNILS,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($HOME_ADDRESS,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($DATE_WORK_DOGOVOR,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($AGREMMENT_GET_EMAIL,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������


########�������� �� ���� ���
if (length($FIO)==0)
{
  my $ans="���������� ��������� \"���\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ���
if (length($FIO)>255)
{
  my $ans="��� �� ����� ���� ������� 255 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ���������
if (length($POSITION)==0)
{
  my $ans="���������� ��������� \"���������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ���������
if (length($POSITION)>255)
{
  my $ans="��������� �� ����� ���� ������� 255 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ��������
if (length($PHONE)==0)
{
  my $ans="���������� ��������� \"�������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������������ ��������
#if (length($PHONE)>0)
#{
#  if ($PHONE!~m/^((8|\+7)[\- ]?)?(\(?\d{2,5}\)?[\- ]?)?[\d\- ]{7,10}$/is)
#  {
#        my $ans="������ ����������� ������ �� ���������!";
#        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
#        my $res=$ans;

#        #convert  data to JSON
#        my $op = JSON -> new -> pretty(1);
#        my $json = $op -> encode({result => $res});

#        print $cgi->header('application/json;charset=windows-1251');
#        print $json;
#        exit;
#  }
#}
##############################################################

########�������� ������ ��������
if (length($PHONE)>20)
{
  my $ans="������� �� ����� ���� ������� 20 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������������ E-Mail
if (length($EMAIL)>0)
{
  if ($EMAIL!~ /^[a-z0-9\.\-_]+\@[a-z0-9\.\-_]+\.[a-z]{2,4}$/i)
  {
        my $ans="��������� EMAIL �� ���������!";
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
##############################################################

########�������� �� ���� �� �������
if (length($DATE_OF_BORN)==0)
{
  my $ans="���������� ��������� \"���� �������� �������������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#�������� ������������ ���� ��������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($DATE_OF_BORN!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� �� ������������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
###########################################################################################################################################
        
# ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_OF_BORN=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� �� ������������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_OF_BORN=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� �� ������������� �� ������� ������� ���.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_OF_BORN=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� �� ������������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########�������� �� ���� ����� �������� 
#if (length($SER_PASSPORT)==0)
#{
#  my $ans="���������� ��������� \"����� ��������\"!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########�������� ������ ����� ��������
#if (length($SER_PASSPORT)>4)
#{
#  my $ans="����� �������� �� ����� ���� ������� 4 ��������!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########�������� �� ���� ������ ���� � ����� ��������
if ($SER_PASSPORT!~m/^\d+$/is)
{
  my $ans="����� �������� ����� ��������� ������ �����!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ������ �������� 
if (length($NUM_PASSPORT)==0)
{
  my $ans="���������� ��������� \"����� ��������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ������ ��������
if (length($NUM_PASSPORT)>6)
{
  my $ans="����� �������� �� ����� ���� ������� 6 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ������ ���� � ������ ��������
if ($NUM_PASSPORT!~m/^\d+$/is)
{
  my $ans="����� �������� ����� ��������� ������ �����!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ��� ����� ������� 
#if (length($KEM_VIDAN)==0)
#{
#  my $ans="���������� ��������� \"��� ����� �������\"!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########�������� ������ ��� ����� �������
if (length($KEM_VIDAN)>255)
{
  my $ans="��� ����� ������� �� ����� ���� ������� 255 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ���� ������ ��������
if (length($KOGDA_VIDAN)==0)
{
  my $ans="���������� ��������� \"���� ������ ��������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#�������� ������������ ���� ������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($KOGDA_VIDAN!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
###########################################################################################################################################
        
# ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$KOGDA_VIDAN=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$KOGDA_VIDAN=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �������� �� ������� ������� ���.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$KOGDA_VIDAN=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########�������� ������ ���� �������������
if (length($KOD_PODRAZDELEN)>7)
{
  my $ans="��� ������������� �� ����� ���� ������� 7 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ���
if (length($INN)>12)
{
  my $ans="��� �� ����� ���� ������� 12 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������������ ���
if (length($INN)>0)
{
  if ($INN!~m/^\d{12}$/ixs)
  {
    my $ans="��������� ��� �� ���������. ��� ������ �������� �� 12 ����!.";
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
##############################################################

########�������� ������ �����
if (length($SNILS)>14)
{
  my $ans="����� �� ����� ���� ������� 14 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������������ �����
if (length($SNILS)>0)
{
  if ($SNILS!~m/^\d{3}[-]\d{3}[-]\d{3}[\s]\d{2}$/ixs)
  {
    my $ans="��������� ����� �� ���������. ����� ������ ����� ������ XXX-XXX-XXX XX!.";
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
##############################################################

########�������� �� ���� ������ 
if (length($HOME_ADDRESS)==0)
{
  my $ans="���������� ��������� \"�������� �����\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ������
if (length($HOME_ADDRESS)>255)
{
  my $ans="�������� ����� �� ����� ���� ������� 255 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ���� ��������� ��������
if (length($DATE_WORK_DOGOVOR)==0)
{
  my $ans="���������� ��������� \"���� ��������� ��������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################


#�������� ������������ ���� ��������� ��������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($DATE_WORK_DOGOVOR!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ��������� �������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
###########################################################################################################################################
        
# ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_WORK_DOGOVOR=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ��������� �������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_WORK_DOGOVOR=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ��������� �������� �� ������� ������� ���.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_WORK_DOGOVOR=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ��������� �������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################


#### ���� ������ ������� �� �����, �.�. �������� �� ����� -1, �� ��������� ������ �� ������� ������ � ������ �������
if ($#DATA_CHILD ne '-1'){

###���������, ��� �� ���� �� ����� ���������.
for (my $u=0; $u<=$#DATA_CHILD; $u++)
{
        if (($DATA_CHILD[$u] eq '') || ($DATA_CHILD[$u] eq ' '))
        {
                my $ans="�� ��������� ��������� ���������� � �����!";
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

##���������, ��������� �� ������� ���� �� �����? �� ������� �� ���� ���� ������ �����)))
for (my $u1=1; $u1<=$#DATA_CHILD; $u1=$u1+2)
{
        ## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
        if ($DATA_CHILD[$u1]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
                my $ans="��������� ���� �� � ������� �� ���������. ������ ������ ����, ��������, 2016-05-30";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        ###########################################################################################################################################
        # ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
        ###########################################################################################################################################
        
        # ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $DATA_CHILD[$u1]=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
                my $ans="� ��������� ���� �� � ������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        # ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $DATA_CHILD[$u1]=~/\d{4}/;
        if ($&>3000)
        {
                my $ans="� ��������� ���� �� � ������� �� ������� ������� ���.";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        # ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $DATA_CHILD[$u1]=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
                my $ans="� ��������� ���� �� � ������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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


###################################���������� UUID ��� ������� ��� � ������� teachers � children_of_teachers. �� ����� ���� ����� ����������� ����� ������� � ��� �����
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #� ������ ���������� ����������� ������
  my @row_uuid = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################


  ###################################��������� ������ � ������� teachers, ����� children_of_teachers � ��������� �� UUID
  #���������� ����� ���������� � ���� Eval � ���������� $@, ���� ��������� ������ �� ����� ���������� SQL ������ � ����� Eval, �� ��������� ����� ��������
 
  my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  eval {  
  #��������� ������ � ������� teachers
  my $sql2="insert into teachers (FIO, POSITION, PHONE, EMAIL, DATE_OF_BORN, SER_PASSPORT, NUM_PASSPORT, KEM_VIDAN, KOGDA_VIDAN, KOD_PODRAZDELEN, INN, SNILS, HOME_ADDRESS, DATE_WORK_DOGOVOR, AGREMMENT_GET_EMAIL, USER_ID, DATETIME_CREATE, UUID_IND) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW(),?)";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($FIO, $POSITION, $PHONE, $EMAIL, $DATE_OF_BORN, $SER_PASSPORT, $NUM_PASSPORT, $KEM_VIDAN, $KOGDA_VIDAN, $KOD_PODRAZDELEN, $INN, $SNILS, $HOME_ADDRESS, $DATE_WORK_DOGOVOR, $AGREMMENT_GET_EMAIL, $us_id, $row_uuid[0]);
    
  #��������� ���� �� ����� �������� � ������� children_of_teachers
  for (my $p=0; $p<=$#DATA_CHILD; $p=$p+2)
  {
         my $sql2="insert into children_of_teachers (FIO, DATE_OF_BORN, USER_ID, DATETIME_CREATE, UUID_IND_TEACHERS) values (?,?,?,NOW(),?)";
         $sth2=$dbh2->prepare($sql2);
         $sth2->execute($DATA_CHILD[$p], $DATA_CHILD[$p+1], $us_id, $row_uuid[0]);
  }
    
  $dbh2->commit; #���������� ����������
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # ���� ��������� ������, �� ���������� ����������
  {
  # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
  eval { $dbh2->rollback; };
  }
  else
  {
    my $ans="������������� � ��� ���� ��������� �������!"; 
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    ############################################################
    exit;
  }
  
  $dbh2->disconnect; 
  ################################################
   
}
else # ��������� ������� ��� �����
{
  ###################################���������� UUID ��� ������� ��� � ������� teachers. � �������� ����� �� �� �����, �.�. ���� UID ������������ ��� ����� ������ � ������� � ��� �����, � ���� ���� ��� ������� ������� ��� �����.
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #� ������ ���������� ����������� ������
  my @row_uuid1 = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################
  
  my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="insert into teachers (FIO, POSITION, PHONE, EMAIL, DATE_OF_BORN, SER_PASSPORT, NUM_PASSPORT, KEM_VIDAN, KOGDA_VIDAN, KOD_PODRAZDELEN, INN, SNILS, HOME_ADDRESS, DATE_WORK_DOGOVOR, AGREMMENT_GET_EMAIL, USER_ID, DATETIME_CREATE, UUID_IND) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW(),?)";
  $sth3=$dbh3->prepare($sql3);
  $sth3->execute($FIO, $POSITION, $PHONE, $EMAIL, $DATE_OF_BORN, $SER_PASSPORT, $NUM_PASSPORT, $KEM_VIDAN, $KOGDA_VIDAN, $KOD_PODRAZDELEN, $INN, $SNILS, $HOME_ADDRESS, $DATE_WORK_DOGOVOR, $AGREMMENT_GET_EMAIL, $us_id, $row_uuid1[0]);

  $dbh3->disconnect;

  my $ans="������������� �������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################
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
