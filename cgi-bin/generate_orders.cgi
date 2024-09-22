#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;
use Encode;
use Spreadsheet::ParseExcel;
use Spreadsheet::ParseExcel::SaveParser;
use Lingua::RU::Num2Word qw/num2rus_cardinal/;
use Date::Calc qw(:all);
use Text::Wrap::Smart qw(wrap_smart);

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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $id=param('id');
my $fio=param('fio');
my $osnovan=param('osnovanie');
my $summ=param('summ');
my $who_get_money=param('who_get_money');
my $date_pay=param('date_pay');
my $num_dog=param('num_dog');
$id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$fio=~s/\0//g; $fio=~s/\.\.//g; $fio=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$osnovan=~s/\0//g; $osnovan=~s/\.\.//g; $osnovan=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$summ=~s/\0//g; $summ=~s/\.\.//g; $summ=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_pay=~s/\0//g; $date_pay=~s/\.\.//g; $date_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$num_dog=~s/\0//g; $num_dog=~s/\.\.//g; $num_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#��������� ����������� �� �����. ������ ������ ����� �� ����� 40 ��������
my @chunks_osnovan = wrap_smart(decode('utf-8', $osnovan),  {no_split => 1, max_msg_size => 40});

#���������� ������� �������� � ��� ��� �������� (�� ������ ������), ���� ������� �������� ������ 18 ���
my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="select DATE_OF_BORN, FIO_PARENT from pupils where Num_dogovor=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($num_dog);
my @data_student = $sth4->fetchrow_array;

my ($today_year,$today_month,$today_day, $hour,$min,$sec) = Today_and_Now(); #���������� ����������� ����, ��������� ������ Date::Calc

#������ ������ ���� �������� �������� ��� ����������� ��� �������� � �����
my @age = ($data_student[0] =~ /^(\d+)\-(\d+)\-(\d+)$/);

#���������� ���� �������� � ����������� ���� ��� ����������� ��������
my ($Dy,$Dm,$Dd) =N_Delta_YMD($age[0],$age[1],$age[2], $today_year,$today_month,$today_day);

my @chunks_fio;
if ($Dy<18)
{
   $fio = decode('windows-1251', $data_student[1]." �� �������� ").decode('utf8', $fio);
   @chunks_fio = wrap_smart($fio,  {no_split => 1, max_msg_size => 40}); #��������� ����������� �� �����. ������ ������ ����� �� ����� 40 ��������
}
else
{
   $fio = decode('utf8', $fio);
   @chunks_fio = wrap_smart($fio,  {no_split => 1, max_msg_size => 40}); #��������� ����������� �� �����. ������ ������ ����� �� ����� 40 ��������
}

#�������������� ���� � ���������� ���, �.�. � ����� ���� ��������� � ������� 2017-01-27
$date_pay=~ s/^(\d+)-(\d+)-(\d+)$/$3.$2.$1/;

my $cgi=CGI->new;

# Open an existing file with SaveParser
my $parser   = Spreadsheet::ParseExcel::SaveParser->new();
my $template = $parser->Parse('../templates/pko_ko-1.xls');
 
# Get the first worksheet.
my $worksheet = $template->worksheet(0);
 
# ��������� ����� ���������
$worksheet->AddCell( 14, 43, $id);
$worksheet->AddCell( 9, 90, $id);

# ��������� ���� ���������
$worksheet->AddCell( 14, 53, $date_pay);
$worksheet->AddCell( 11, 71, $date_pay);
$worksheet->AddCell( 28, 69, $date_pay);

# ��������� �� ���� ��������
$worksheet->AddCell(22, 8, $fio); 
#$worksheet->AddCell(13, 76, $fio); 
$worksheet->AddCell(13, 76, $chunks_fio[0]); 
$worksheet->AddCell(14, 68, $chunks_fio[1]." ".$chunks_fio[2]); 

# ��������� ���������
$osnovan = decode('utf8', $osnovan);
$worksheet->AddCell(24, 8, $osnovan); 
#$worksheet->AddCell(15, 75, $osnovan); 
$worksheet->AddCell(15, 75, $chunks_osnovan[0]);
$worksheet->AddCell(16, 68, $chunks_osnovan[1]." ".$chunks_osnovan[2]);

# ��������� �����
$worksheet->AddCell(20, 38, $summ);  
$worksheet->AddCell(20, 73, $summ);  

# ��������� ����� ��������
my $sum_propis=num2rus_cardinal($summ, 'NEUTER'); 
$worksheet->AddCell(26, 5, ucfirst($sum_propis));  
$worksheet->AddCell(22, 68, ucfirst($sum_propis));  

# ��������� ��� ������ ������
$who_get_money = decode('utf8', $who_get_money);
$worksheet->AddCell(35, 85, $who_get_money); 
$worksheet->AddCell(35, 25, $who_get_money); 


# Write over the existing file or write a new file.
$template->SaveAs('../orders/order_'.$id.'.xls');

my $ans="����� ����������� ���������! <a href=\"../orders/order_$id.xls\">������� �����</a>";
#Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
#         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }
}
else { print "Location: http://localhost:6080\n\n"; }


__END__