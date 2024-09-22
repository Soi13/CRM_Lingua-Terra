package Build_Menu;
use strict;
use DBI;
use CGI::Carp qw(fatalsToBrowser);
use ConnectDB;
use Carp;
require Exporter;

my @ISA=qw(Exporter);
my @EXPORT=qw(menu);
my @EXPORT_OK=qw($idd, $SID);



sub menu
{

my @idd=@_; #В этот массив загружается ID пользовтеля переданная с вызываемого скрипта, ID лежит в массиве во втором элементе ,т.е. в $idd[1]
my $data;
my $dbh=ConnectDB->connect;
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select * from usr where ID like ?";
$sth=$dbh->prepare($sql);
$sth->execute($idd[1]); #ID лежит в массиве во втором элементе ,т.е. в $idd[1]

my @row = $sth->fetchrow_array; #Результат запроса записываем в массив

$dbh->disconnect;
   
   ##################Раздел меню СЕКРЕТАРИАТ#################################
   if ($row[5]==1 && $row[6]==1 && $row[7]==1 && $row[8]==1 && $row[9]==1 && $row[10]==1 && $row[11]==1 && $row[12]==1 && $row[13]==1 && $row[14]==1 && $row[15]==1 && $row[16]==1 && $row[17]==1 && $row[47]==1 && $row[52]==1 && $row[58]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Секретариат</span></a>
            <ul>
               <li><a href='sekretariat_main.cgi?SID=$idd[2]'><span>Главная</span></a></li>
               <li><a href='sekretariat_groups.cgi?SID=$idd[2]'><span>Группы</span></a></li>
               <li><a href='sekretariat_students.cgi?SID=$idd[2]'><span>Студенты</span></a></li>
               <li><a href='sekretariat_teachers.cgi?SID=$idd[2]'><span>Учителя</span></a></li>
               <li><a href='sekretariat_rooms.cgi?SID=$idd[2]'><span>Кабинеты</span></a></li>
               <li><a href='sekretariat_calendar.cgi?SID=$idd[2]'><span>Календарь</span></a></li>
			   <li><a href='sekretariat_personal_calendar.cgi?SID=$idd[2]'><span>Личный календарь</span></a></li>
               <li><a href='#'><span>Фирмы</span></a></li>
               <li><a href='#'><span>Связь</span></a></li>
               <li><a href='sekretariat_sms.cgi?SID=$idd[2]'><span>СМС</span></a></li>
               <li><a href='sekretariat_documents.cgi?SID=$idd[2]'><span>Документы</span></a></li>
               <li><a href='#'><span>Пользователи</span></a></li>
               <li><a href='sekretariat_zayavki.cgi?SID=$idd[2]'><span>Заявки</span></a></li>
			   <li><a href='sekretariat_reserv.cgi?SID=$idd[2]'><span>Резерв</span></a></li>
               <li class='last'><a href='#'><span>Настройки</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[5]==1 && ($row[6]!=1 || $row[7]!=1 || $row[8]!=1 || $row[9]!=1 || $row[10]!=1 || $row[11]!=1 || $row[12]!=1 || $row[13]!=1 || $row[14]!=1 || $row[15]!=1 || $row[16]!=1 || $row[17]!=1 || $row[47]!=1 || $row[52]!=1 || $row[58]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Секретариат</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='sekretariat_main.cgi?SID=$idd[2]'><span>Главная</span></a></li>\n) if ($row[6]==1);
         print qq(<li><a href='sekretariat_groups.cgi?SID=$idd[2]'><span>Группы</span></a></li>\n) if ($row[7]==1);
         print qq(<li><a href='sekretariat_students.cgi?SID=$idd[2]'><span>Студенты</span></a></li>\n) if ($row[8]==1);
         print qq(<li><a href='sekretariat_teachers.cgi?SID=$idd[2]'><span>Учителя</span></a></li>\n) if ($row[9]==1);
         print qq(<li><a href='sekretariat_rooms.cgi?SID=$idd[2]'><span>Кабинеты</span></a></li>\n) if ($row[10]==1);
         print qq(<li><a href='sekretariat_calendar.cgi?SID=$idd[2]'><span>Календарь</span></a></li>\n) if ($row[11]==1);
		 print qq(<li><a href='sekretariat_personal_calendar.cgi?SID=$idd[2]'><span>Личный календарь</span></a></li>\n) if ($row[52]==1);
         print qq(<li><a href='#'><span>Фирмы</span></a></li>\n) if ($row[12]==1);
         print qq(<li><a href='#'><span>Связь</span></a></li>\n) if ($row[13]==1);
         print qq(<li><a href='sekretariat_sms.cgi?SID=$idd[2]'><span>СМС</span></a></li>\n) if ($row[14]==1);
         print qq(<li><a href='sekretariat_documents.cgi?SID=$idd[2]'><span>Документы</span></a></li>\n) if ($row[15]==1);
         print qq(<li><a href='#'><span>Пользователи</span></a></li>\n) if ($row[16]==1);
         print qq(<li><a href='sekretariat_zayavki.cgi?SID=$idd[2]'><span>Заявки</span></a></li>\n) if ($row[47]==1);
		 print qq(<li><a href='sekretariat_reserv.cgi?SID=$idd[2]'><span>Резерв</span></a></li>\n) if ($row[58]==1);
         print qq(<li><a href='#'><span>Настройки</span></a></li>\n) if ($row[17]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################Раздел меню ФИНАНСЫ#################################
   if ($row[18]==1 && $row[19]==1 && $row[20]==1 && $row[21]==1 && $row[22]==1 && $row[23]==1 && $row[51]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Финансы</span></a>
            <ul>
               <li><a href='#'><span>Транзакции</span></a></li>
               <li><a href='#'><span>Счет-фактуры</span></a></li>
               <li><a href='finance_orders.cgi?SID=$idd[2]'><span>Приходные ордера</span></a></li>
               <li><a href='finance_import_from_bank.cgi?SID=$idd[2]'><span>Импорт файлов из банка</span></a></li>
			   <li><a href='finance_export_2_bank.cgi?SID=$idd[2]'><span>Экспорт файлов в банк</span></a></li>
               <li class='last'><a href='#'><span>Настройки</span></a></li>             
            </ul>
         </li>
HTML
   }
   elsif ($row[18]==1 && ($row[19]!=1 || $row[20]!=1 || $row[21]!=1 || $row[22]!=1 || $row[23]!=1 || $row[51]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Финансы</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Транзакции</span></a></li>\n) if ($row[19]==1);
         print qq(<li><a href='#'><span>Счет-фактуры</span></a></li>\n) if ($row[20]==1);
         print qq(<li><a href='finance_orders.cgi?SID=$idd[2]'><span>Приходные ордера</span></a></li>\n) if ($row[21]==1);
         print qq(<li><a href='finance_import_from_bank.cgi?SID=$idd[2]'><span>Импорт файлов из банка</span></a></li>\n) if ($row[22]==1);
		 print qq(<li><a href='finance_export_2_bank.cgi?SID=$idd[2]'><span>Экспорт файлов в банк</span></a></li>\n) if ($row[51]==1);
         print qq(<li><a href='#'><span>Настройки</span></a></li>\n) if ($row[23]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################Раздел меню РЕГИСТРАЦИЯ#################################
   if ($row[24]==1 && $row[25]==1 && $row[26]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Регистрация</span></a>
            <ul>
               <li><a href='#'><span>Формуляры</span></a></li>
               <li class='last'><a href='#'><span>Настройки</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[24]==1 && ($row[25]!=1 || $row[26]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Регистрация</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Формуляры</span></a></li>\n) if ($row[25]==1);
         print qq(<li><a href='#'><span>Настройки</span></a></li>\n) if ($row[26]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################Раздел меню E-LEARNING#################################
   if ($row[27]==1 && $row[28]==1 && $row[29]==1 && $row[30]==1 && $row[31]==1 && $row[32]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>E-learning</span></a>
            <ul>
               <li><a href='#'><span>Тесты</span></a></li>
               <li><a href='#'><span>Этикетки</span></a></li>
               <li><a href='#'><span>Файлы филиала</span></a></li>
               <li><a href='#'><span>Файлы</span></a></li>
               <li class='last'><a href='#'><span>Файлы учителей</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[27]==1 && ($row[28]!=1 || $row[29]!=1 || $row[30]!=1 || $row[31]!=1 || $row[32]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>E-learning</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Тесты</span></a></li>\n) if ($row[28]==1);
         print qq(<li><a href='#'><span>Этикетки</span></a></li>\n) if ($row[29]==1);
         print qq(<li><a href='#'><span>Файлы филиала</span></a></li>\n) if ($row[30]==1);
         print qq(<li><a href='#'><span>Файлы</span></a></li>\n) if ($row[31]==1);
         print qq(<li><a href='#'><span>Файлы учителей</span></a></li>\n) if ($row[32]==1);         
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################
   
   
##################Раздел меню Мультимедиатека#################################
   if ($row[33]==1 && $row[34]==1 && $row[35]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Мультимедиатека</span></a>
            <ul>
               <li><a href='#'><span>Список позиций</span></a></li>
               <li class='last'><a href='#'><span>Настройки</span></a></li>               
            </ul>
         </li>
HTML
   }       
   elsif ($row[33]==1 && ($row[34]!=1 || $row[35]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Мультимедиатека</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Список позиций</span></a></li>\n) if ($row[34]==1);
         print qq(<li><a href='#'><span>Настройки</span></a></li>\n) if ($row[35]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################   


##################Раздел меню Супрерадмин#################################
   if ($row[36]==1 && $row[37]==1 && $row[38]==1 && $row[39]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Суперадмин</span></a>
            <ul>
               <li><a href='#'><span>Филиалы</span></a></li>
               <li><a href='#'><span>Суперадминистраторы</span></a></li>
               <li class='last'><a href='administration_tools.cgi?SID=$idd[2]'><span>Настройки</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[36]==1 && ($row[37]!=1 || $row[38]!=1 || $row[39]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Суперадмин</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Филиалы</span></a></li>\n) if ($row[37]==1);
         print qq(<li><a href='#'><span>Суперадминистраторы</span></a></li>\n) if ($row[38]==1);
         print qq(<li><a href='administration_tools.cgi?SID=$idd[2]'><span>Настройки</span></a></li>\n) if ($row[39]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################Раздел меню Отчеты#################################
   if ($row[40]==1 && $row[41]==1 && $row[60]==1 && $row[61]==1 && $row[62]==1 && $row[66]==1 && $row[68]==1 && $row[73]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Отчеты</span></a>
            <ul>
               <li><a href='reports_debts_4_today.cgi?SID=$idd[2]'><span>Должники на сегодня</span></a></li>
			   <li><a href='reports_debts_month.cgi?SID=$idd[2]'><span>Должники за месяц</span></a></li>
			   <li><a href='reports_plan_fact_branch.cgi?SID=$idd[2]'><span>План-Факт по филиалам (за период)</span></a></li>
			   <li><a href='reports_plan_fact_branch_real_pays.cgi?SID=$idd[2]'><span>Реальные поступления за месяц по филиалам</span></a></li>
			   <li><a href='reports_students_teachers.cgi?SID=$idd[2]'><span>Студенты/Преподаватели</span></a></li>
			   <li class='last'><a href='reports_students_age.cgi?SID=$idd[2]'><span>Студенты по возрасту</span></a></li>
			   <li class='last'><a href='reports_students_dogovors.cgi?SID=$idd[2]'><span>Студенты/Договоры</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[40]==1 && ($row[41]!=1 || $row[60]!=1 || $row[61]!=1 || $row[62]!=1 || $row[66]!=1 || $row[68]!=1 || $row[73]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Отчеты</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='reports_debts_4_today.cgi?SID=$idd[2]'><span>Должники на сегодня</span></a></li>\n) if ($row[41]==1);
		 print qq(<li><a href='reports_debts_month.cgi?SID=$idd[2]'><span>Должники за месяц</span></a></li>\n) if ($row[60]==1);         
		 print qq(<li><a href='reports_plan_fact_branch.cgi?SID=$idd[2]'><span>План-Факт по филиалам (за период)</span></a></li>\n) if ($row[61]==1);
		 print qq(<li><a href='reports_plan_fact_branch_real_pays.cgi?SID=$idd[2]'><span>Реальные поступления за месяц по филиалам</span></a></li>\n) if ($row[62]==1);         
		 print qq(<li><a href='reports_students_teachers.cgi?SID=$idd[2]'><span>Студенты/Преподаватели</span></a></li>\n) if ($row[66]==1);
		 print qq(<li><a href='reports_students_age.cgi?SID=$idd[2]'><span>Студенты по возрасту</span></a></li>\n) if ($row[68]==1);
		 print qq(<li><a href='reports_students_dogovors.cgi?SID=$idd[2]'><span>Студенты/Договоры</span></a></li>\n) if ($row[73]==1);  
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################Раздел меню E-журнал#################################
   if ($row[42]==1)
   {
      print qq (<li><a href='#'><span>E-журнал</span></a></li>);
   }
   ##########################################################################


##################Раздел меню Контроллер#################################
   if ($row[43]==1)
   {
      print qq (<li><a href='#'><span>Контроллер</span></a></li>);
   }
   ##########################################################################


##################Раздел меню Отчеты#################################
   if ($row[44]==1 && $row[45]==1 && $row[46]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>Анкеты</span></a>
            <ul>
               <li><a href='#'><span>Анкеты</span></a></li>
               <li class='last'><a href='#'><span>Этикетки</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[44]==1 && ($row[45]!=1 || $row[46]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>Анкеты</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>Анкеты</span></a></li>\n) if ($row[45]==1);
         print qq(<li><a href='#'><span>Этикетки</span></a></li>\n) if ($row[46]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################
}

__END__


