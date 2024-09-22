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
use Spreadsheet::WriteExcel;

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
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $data=param('data');
my $period=param('period');

$data=~s/\0//g; $data=~s/\.\.//g; $data=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$period=~s/\0//g; $period=~s/\.\.//g; $period=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($period,'utf8','windows-1251');

my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year=$year+1900;

#$data = encode_utf8($data);
my $perl_hash = decode_json($data);
#my $rres=$perl_hash->{"rows"}[0]{fio};
my $len_array=scalar @{$perl_hash->{"rows"}}; #�������� ������ ������� �����, ������� ��� (������) ��������� � ����

my $workbook = Spreadsheet::WriteExcel->new('../reports/report_'.$hour.$min.$sec.'.xls');
my $worksheet = $workbook->add_worksheet('Report');
$worksheet->set_landscape(); 
$worksheet->set_column(0,0,12);
$worksheet->set_column(1,0,35);
$worksheet->set_column(2,0,14); 

my $tabformat = $workbook->add_format();
$tabformat->set_border();

#������ ��� ���������
my $format = $workbook->add_format();
$format->set_bold();
$format->set_color('blue');
$format->set_align('center');
$format->set_size(20);
$format->set_font('Times New Roman');

#������ ��� ��������� �������
my $format_tab = $workbook->add_format();
$format_tab->set_bold();
$format_tab->set_align('center');
$format_tab->set_font('Times New Roman');

#������ ������ �������������
my $format_tech = $workbook->add_format();
$format_tech->set_bold();
$format_tech->set_align('left');
$format_tech->set_font('Times New Roman');

$worksheet->write(1, 1, decode('windows-1251', "�������� �� ".$period), $format);
$worksheet->write(3, 0, decode('windows-1251', "���������"), $format_tab);
$worksheet->write(3, 1, decode('windows-1251', "���"), $format_tab);
$worksheet->write(3, 2, decode('windows-1251', "����� �����"), $format_tab);


my $res_sum=0;
my $cnt=0;
for (my $h=0; $h<=$len_array-1; $h++)
{
        #���� � ���� �� ������� �������� ������� ���������� �� �����
        $worksheet->write($h+4, 0, $perl_hash->{"rows"}[$h]{"nm_dg"}, $tabformat);
        $worksheet->write($h+4, 1, $perl_hash->{"rows"}[$h]{"fio"}, $tabformat);
        $worksheet->write($h+4, 2, $perl_hash->{"rows"}[$h]{"summ"}, $tabformat);
        $res_sum=$res_sum+$perl_hash->{"rows"}[$h]{"summ"};
        $cnt=$h+5;
}
$worksheet->write($cnt, 1, decode('windows-1251',"�����:"), $tabformat);
$worksheet->write($cnt, 2, $res_sum, $tabformat);

my $cgi=CGI->new;

my $ans="����� �����������! <a href=\"../reports/report_$hour$min$sec.xls\">������� �����</a>";
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
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
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
else { print "Location: http://teachers.localhost:6080\n\n"; }


__END__