#!/usr/bin/perl

use Dough::CGI;
use Dough::Log;
use Dough::Config;

print "Key: $k_awsKey\n";
print "$k_logFile\n";

my $log = Dough::Log->instance();
print "Log: $log\n";
$log->log("A log message: $k_awsSec");

my $cgi = Dough::CGI->new();
$cgi->processQuery();
