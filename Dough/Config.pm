package Dough::Config;

use Exporter qw(import);
@EXPORT = qw($k_awsKey $k_awsSec $k_awsTADom $k_awsUserDom $k_logFile 
             $k_whereConcreteSaveKeys $k_hashSubstrLength $k_placeholderURL);

our $k_awsKey = "0639RVH93HXWSTAP9WG2";
our $k_awsSec = "67eHsTHoFWAgWqE/EluaqQAtalEF8P+Ni7upo3PV";
our $k_awsTADom = 'Dough_Transactions_Test';
our $k_awsUserDom = 'Dough_Users_Test';

our $k_logFile = '/home/sulciphur/wlogs/doughBridge.log';

our $k_hashSubstrLength = 15;
our $k_whereConcreteSaveKeys = {url => 1, staticMapUrl => 1, titleNoFormatting => 1, 
    city => 1, region => 1,  country => 1,  streetAddress => 1};

our $k_placeholderURL = '/nada.html';

1;
