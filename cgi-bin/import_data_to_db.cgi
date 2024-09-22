#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use Spreadsheet::ParseExcel;
use Encode qw(encode decode is_utf8);

my $parser   = Spreadsheet::ParseExcel->new();
my $workbook = $parser->parse('/home/a0018982/domains/linguaterra-soft.ru/public_html/pupils1.xls');

if ( !defined $workbook ) {
    die $parser->error(), ".\n";
}

  my $worksheet = $workbook->worksheet(0);

my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth2=$dbh2->do("SET NAMES 'cp1251'");

my $str_cell3;my $str_cell4;
my $str_cell5;
my $str_cell6;
my $str_cell7;
my $str_cell8;
my $str_cell9;my $str_cell10;
my $str_cell11;
my $str_cell12;my $str_cell13;
my $str_cell14;
my $str_cell15;
#my $str_cell16;
my $str_cell17;
my $str_cell18;

for (my $t=1; $t<=1350; $t++)
{
my $cell = $worksheet->get_cell($t, 0); #Номер договора
my $cell1 = $worksheet->get_cell($t, 1); #ФИО
my $cell2 = $worksheet->get_cell($t, 3); #Дата рождения
my $cell3 = $worksheet->get_cell($t, 4); #Место работы/учебы
my $cell4 = $worksheet->get_cell($t, 5); #Должность факультет
my $cell5 = $worksheet->get_cell($t, 6); #Адрес
my $cell6 = $worksheet->get_cell($t, 7); #Моб тел
my $cell7 = $worksheet->get_cell($t, 8); #Дом тел
my $cell8 = $worksheet->get_cell($t, 9); #Раб тел
my $cell9 = $worksheet->get_cell($t, 10); #Email
my $cell10 = $worksheet->get_cell($t, 14); #Ser Passport
my $cell11 = $worksheet->get_cell($t, 18); #Source about us
my $cell12 = $worksheet->get_cell($t, 19); #Date of filling
my $cell13 = $worksheet->get_cell($t, 43); #Fio parent
my $cell14 = $worksheet->get_cell($t, 48); #Num passport
my $cell15 = $worksheet->get_cell($t, 49); #Kem vidan passport
#my $cell16 = $worksheet->get_cell($t, 50); #Kogda vidan passport
my $cell17 = $worksheet->get_cell($t, 51); #Пол
my $cell18 = $worksheet->get_cell($t, 52); #Филиал
my $str_cell = encode('cp1251', $cell->Value); my $str_cell1 = encode('cp1251', $cell1->Value); 
my $str_cell2 = encode('cp1251', $cell2->Value);
if (defined($cell3)) { $str_cell3 = encode('cp1251', $cell3->Value); } else { $str_cell3=""; } 
if (defined($cell4)) { $str_cell4 = encode('cp1251', $cell4->Value); } else { $str_cell4=""; }
if (defined($cell5)) { $str_cell5 = encode('cp1251', $cell5->Value); } else { $str_cell5=""; }
if (defined($cell6)) { $str_cell6 = encode('cp1251', $cell6->Value); $str_cell6=~s/,//ig } else { $str_cell6=""; }
if (defined($cell7)) { $str_cell7 = encode('cp1251', $cell7->Value); } else { $str_cell7=""; }
if (defined($cell8)) { $str_cell8 = encode('cp1251', $cell8->Value); } else { $str_cell8=""; }
if (defined($cell9)) { $str_cell9 = encode('cp1251', $cell9->Value); } else { $str_cell9=""; }
if (defined($cell10)) { $str_cell10 = encode('cp1251', $cell10->Value); if (length($str_cell10)>4) { $str_cell10=""; } } else { $str_cell10=""; }
if (defined($cell11)) { $str_cell11 = encode('cp1251', $cell11->Value); } else { $str_cell11=""; }
if (defined($cell12)) { $str_cell12 = encode('cp1251', $cell12->Value); } else { $str_cell12=""; }
if (defined($cell13)) { $str_cell13 = encode('cp1251', $cell13->Value); } else { $str_cell13=""; }
if (defined($cell14)) { $str_cell14 = encode('cp1251', $cell14->Value); } else { $str_cell14=""; }
if (defined($cell15)) { $str_cell15 = encode('cp1251', $cell15->Value); } else { $str_cell15=""; }
#if (defined($cell16)) { $str_cell16 = encode('cp1251', $cell16->Value); } else { $str_cell16=""; }
if (defined($cell17)) { $str_cell17 = encode('cp1251', $cell17->Value); } else { $str_cell17=""; }
if (defined($cell18)) { $str_cell18 = encode('cp1251', $cell18->Value); } else { $str_cell18=""; }

#my $sql2="insert into pupils (Num_dogovor, FIO, DATE_OF_BORN, PLACE_OF_WORK, POSITION_FACULT, HOME_ADDRESS, MOBILE_PHONE, HOME_PHONE, WORK_PHONE, EMAIL, PASSPORT, SOURCE_ABOUT_US, DATE_OF_FILLING, FIO_PARENT, PASSPORT_NUM, PASSPORT_VIDAN, PASSPORT_DATE, SEX, BRANCH, USER_ID) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";  
my $sql2="insert into pupils (Num_dogovor, FIO, DATE_OF_BORN, PLACE_OF_WORK, POSITION_FACULT, HOME_ADDRESS, MOBILE_PHONE, HOME_PHONE, WORK_PHONE, EMAIL, PASSPORT, SOURCE_ABOUT_US, DATE_OF_FILLING, FIO_PARENT, PASSPORT_NUM, PASSPORT_VIDAN, SEX, BRANCH) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";  
$sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
#$sth2->execute($str_cell, $str_cell1, $cell2, $str_cell3, $str_cell4, $str_cell5, $str_cell6, $str_cell7, $str_cell8, $str_cell9, $str_cell11, $str_cell12, $str_cell13, $str_cell14, $str_cell15, $str_cell16, $str_cell17, $str_cell18, $str_cell19, '3');    
$sth2->execute($str_cell, $str_cell1, $str_cell2, $str_cell3, $str_cell4, $str_cell5, $str_cell6, $str_cell7, $str_cell8, $str_cell9, $str_cell10, $str_cell11, $str_cell12, $str_cell13, $str_cell14, $str_cell15, $str_cell17, $str_cell18);
  #print $t, "\n";
}
$dbh2->disconnect; 

print "Content-type: text/html\n\n";
print "<html><head><title>Installed Perl Modules</title></head><body><table width=\"300px\" border=1><td><tr><td>Module</td> <td>Version</td>";

print "</table></body></html>";