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

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');

#Смотрим определены ли логин и пароль пользователя в сесии
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
my $len_array=scalar @{$perl_hash->{"rows"}}; #Получаем длинну массива хешей, который сам (массив) находится в хеше

my $workbook = Spreadsheet::WriteExcel->new('../reports/report_'.$hour.$min.$sec.'.xls');
my $worksheet = $workbook->add_worksheet('Report');
$worksheet->set_landscape(); 
$worksheet->set_column(0,0,35);
$worksheet->set_column(1,0,5);
$worksheet->set_column(2,0,5); 
$worksheet->set_column(3,0,5); 
$worksheet->set_column(4,0,5); 
$worksheet->set_column(5,0,5); 
$worksheet->set_column(6,0,5); 
$worksheet->set_column(7,0,5); 
$worksheet->set_column(8,0,5); 
$worksheet->set_column(9,0,5); 
$worksheet->set_column(10,0,6); 
$worksheet->set_column(11,0,6); 
$worksheet->set_column(12,0,6); 
$worksheet->set_column(13,0,6); 
$worksheet->set_column(14,0,6); 
$worksheet->set_column(15,0,6); 
$worksheet->set_column(16,0,6); 
$worksheet->set_column(17,0,6); 
$worksheet->set_column(18,0,6); 
$worksheet->set_column(19,0,6); 
$worksheet->set_column(20,0,6); 
$worksheet->set_column(21,0,6); 
$worksheet->set_column(22,0,6); 
$worksheet->set_column(23,0,6); 
$worksheet->set_column(24,0,6); 
$worksheet->set_column(25,0,6); 
$worksheet->set_column(26,0,6); 
$worksheet->set_column(27,0,6); 
$worksheet->set_column(28,0,6); 
$worksheet->set_column(29,0,6); 
$worksheet->set_column(30,0,6); 
$worksheet->set_column(31,0,6); 
$worksheet->set_column(32,0,40);

my $tabformat = $workbook->add_format();
$tabformat->set_border();

#Формат для заголовка
my $format = $workbook->add_format();
$format->set_bold();
$format->set_color('blue');
$format->set_align('center');
$format->set_size(20);
$format->set_font('Times New Roman');

#Формат для заголовка таблицы
my $format_tab = $workbook->add_format();
$format_tab->set_bold();
$format_tab->set_align('center');
$format_tab->set_font('Times New Roman');

#Формат строки Преподаватель
my $format_tech = $workbook->add_format();
$format_tech->set_bold();
$format_tech->set_align('left');
$format_tech->set_font('Times New Roman');

$worksheet->write(1, 1, decode('windows-1251', "Visits of students. Period: ".$period), $format);
$worksheet->write(3, 0, decode('windows-1251', "FIO"), $format_tab);
$worksheet->write(3, 1, decode('windows-1251', "DAY1"), $format_tab);
$worksheet->write(3, 2, decode('windows-1251', "DAY2"), $format_tab);
$worksheet->write(3, 3, decode('windows-1251', "DAY3"), $format_tab);
$worksheet->write(3, 4, decode('windows-1251', "DAY4"), $format_tab);
$worksheet->write(3, 5, decode('windows-1251', "DAY5"), $format_tab);
$worksheet->write(3, 6, decode('windows-1251', "DAY6"), $format_tab);
$worksheet->write(3, 7, decode('windows-1251', "DAY7"), $format_tab);
$worksheet->write(3, 8, decode('windows-1251', "DAY8"), $format_tab);
$worksheet->write(3, 9, decode('windows-1251', "DAY9"), $format_tab);
$worksheet->write(3, 10, decode('windows-1251', "DAY10"), $format_tab);
$worksheet->write(3, 11, decode('windows-1251', "DAY11"), $format_tab);
$worksheet->write(3, 12, decode('windows-1251', "DAY12"), $format_tab);
$worksheet->write(3, 13, decode('windows-1251', "DAY13"), $format_tab);
$worksheet->write(3, 14, decode('windows-1251', "DAY14"), $format_tab);
$worksheet->write(3, 15, decode('windows-1251', "DAY15"), $format_tab);
$worksheet->write(3, 16, decode('windows-1251', "DAY16"), $format_tab);
$worksheet->write(3, 17, decode('windows-1251', "DAY17"), $format_tab);
$worksheet->write(3, 18, decode('windows-1251', "DAY18"), $format_tab);
$worksheet->write(3, 19, decode('windows-1251', "DAY19"), $format_tab);
$worksheet->write(3, 20, decode('windows-1251', "DAY20"), $format_tab);
$worksheet->write(3, 21, decode('windows-1251', "DAY21"), $format_tab);
$worksheet->write(3, 22, decode('windows-1251', "DAY22"), $format_tab);
$worksheet->write(3, 23, decode('windows-1251', "DAY23"), $format_tab);
$worksheet->write(3, 24, decode('windows-1251', "DAY24"), $format_tab);
$worksheet->write(3, 25, decode('windows-1251', "DAY25"), $format_tab);
$worksheet->write(3, 26, decode('windows-1251', "DAY26"), $format_tab);
$worksheet->write(3, 27, decode('windows-1251', "DAY27"), $format_tab);
$worksheet->write(3, 28, decode('windows-1251', "DAY28"), $format_tab);
$worksheet->write(3, 29, decode('windows-1251', "DAY29"), $format_tab);
$worksheet->write(3, 30, decode('windows-1251', "DAY30"), $format_tab);
$worksheet->write(3, 31, decode('windows-1251', "DAY31"), $format_tab);
$worksheet->write(3, 32, decode('windows-1251', "NOTES"), $format_tab);


my $res_sum=0;
my $cnt=0;
for (my $h=0; $h<=$len_array-1; $h++)
{
        #Идем в хеше по каждому элементу массива состоящего их хешей
        $worksheet->write($h+4, 0, $perl_hash->{"rows"}[$h]{"FIO"}, $tabformat);
        $worksheet->write($h+4, 1, $perl_hash->{"rows"}[$h]{"DAY1"}, $tabformat);
        $worksheet->write($h+4, 2, $perl_hash->{"rows"}[$h]{"DAY2"}, $tabformat);
        $worksheet->write($h+4, 3, $perl_hash->{"rows"}[$h]{"DAY3"}, $tabformat);
        $worksheet->write($h+4, 4, $perl_hash->{"rows"}[$h]{"DAY4"}, $tabformat);
        $worksheet->write($h+4, 5, $perl_hash->{"rows"}[$h]{"DAY5"}, $tabformat);
        $worksheet->write($h+4, 6, $perl_hash->{"rows"}[$h]{"DAY6"}, $tabformat);
        $worksheet->write($h+4, 7, $perl_hash->{"rows"}[$h]{"DAY7"}, $tabformat);
        $worksheet->write($h+4, 8, $perl_hash->{"rows"}[$h]{"DAY8"}, $tabformat);
        $worksheet->write($h+4, 9, $perl_hash->{"rows"}[$h]{"DAY9"}, $tabformat);
        $worksheet->write($h+4, 10, $perl_hash->{"rows"}[$h]{"DAY10"}, $tabformat);
        $worksheet->write($h+4, 11, $perl_hash->{"rows"}[$h]{"DAY11"}, $tabformat);
        $worksheet->write($h+4, 12, $perl_hash->{"rows"}[$h]{"DAY12"}, $tabformat);
        $worksheet->write($h+4, 13, $perl_hash->{"rows"}[$h]{"DAY13"}, $tabformat);
        $worksheet->write($h+4, 14, $perl_hash->{"rows"}[$h]{"DAY14"}, $tabformat);
        $worksheet->write($h+4, 15, $perl_hash->{"rows"}[$h]{"DAY15"}, $tabformat);
        $worksheet->write($h+4, 16, $perl_hash->{"rows"}[$h]{"DAY16"}, $tabformat);
        $worksheet->write($h+4, 17, $perl_hash->{"rows"}[$h]{"DAY17"}, $tabformat);
        $worksheet->write($h+4, 18, $perl_hash->{"rows"}[$h]{"DAY18"}, $tabformat);
        $worksheet->write($h+4, 19, $perl_hash->{"rows"}[$h]{"DAY19"}, $tabformat);
        $worksheet->write($h+4, 20, $perl_hash->{"rows"}[$h]{"DAY20"}, $tabformat);
        $worksheet->write($h+4, 21, $perl_hash->{"rows"}[$h]{"DAY21"}, $tabformat);
        $worksheet->write($h+4, 22, $perl_hash->{"rows"}[$h]{"DAY22"}, $tabformat);
        $worksheet->write($h+4, 23, $perl_hash->{"rows"}[$h]{"DAY23"}, $tabformat);
        $worksheet->write($h+4, 24, $perl_hash->{"rows"}[$h]{"DAY24"}, $tabformat);
        $worksheet->write($h+4, 25, $perl_hash->{"rows"}[$h]{"DAY25"}, $tabformat);
        $worksheet->write($h+4, 26, $perl_hash->{"rows"}[$h]{"DAY26"}, $tabformat);
        $worksheet->write($h+4, 27, $perl_hash->{"rows"}[$h]{"DAY27"}, $tabformat);
        $worksheet->write($h+4, 28, $perl_hash->{"rows"}[$h]{"DAY28"}, $tabformat);
        $worksheet->write($h+4, 29, $perl_hash->{"rows"}[$h]{"DAY29"}, $tabformat);
        $worksheet->write($h+4, 30, $perl_hash->{"rows"}[$h]{"DAY30"}, $tabformat);
        $worksheet->write($h+4, 31, $perl_hash->{"rows"}[$h]{"DAY31"}, $tabformat);      
        $worksheet->write($h+4, 32, $perl_hash->{"rows"}[$h]{"NOTES"}, $tabformat);    
        
        #$cnt=$h+5;
}
#$worksheet->write($cnt, 1, decode('windows-1251',"Итого:"), $tabformat);
#$worksheet->write($cnt, 2, $res_sum, $tabformat);

my $cgi=CGI->new;

my $ans="Отчет сформирован! <a href=\"../reports/report_$hour$min$sec.xls\">Открыть отчет</a>";
#Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
         print "Set-Cookie: $cookies\n";
#         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
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