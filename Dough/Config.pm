package Dough::Config;

use Exporter qw(import);
@EXPORT = qw($k_awsKey $k_awsSec $k_awsTADom $k_awsUserDom $k_logFile);

our $k_awsKey = "0639RVH93HXWSTAP9WG2";
our $k_awsSec = "67eHsTHoFWAgWqE/EluaqQAtalEF8P+Ni7upo3PV";
our $k_awsTADom = 'Dough_Transactions_Test';
our $k_awsUserDom = 'Dough_Users_Test';

our $k_logFile = '/tmp/doughBridge.log';

1;
