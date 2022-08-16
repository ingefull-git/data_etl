# Power Queries Pull Generic implementations

## Copying the script
in order to copy the file into /usr/bin folder of each server I have created a _new copy of the script, then copied it to one district folder within the /home/ folder and finally copied it to the _generic version within /usr/bin/ folder.
This way we avoid overwriting the _generic version possibly in place and being used by the scheduled tasks until we actually test the new one.

- cp /home/5121/powerQueriesPull_new.py /usr/bin/powerQueriesPull_generic.py

## Executing the file from a scheduled task

Create a task schedule and include the command. For different options, please refer to the script itself, it contains an usage section at the beggining.

- ptpython /usr/bin/powerQueriesPull_generic.py -f 5121

## List of districts using unified powerQueriesPull_generic

| Server | Districts                                    | PSID   | Version | Date       | Folder |
| ------ | -------------------------------------------- | ------ | ------- | ---------- | ------ |
| PT04-1 | BRUNSWICK COUNTY SCHOOLS                     | 315721 | 1.2.0   | 2021-12-23 |  5990  |
| PT04-1 | AIKEN COUNTY SCHOOL DISTRICT                 | 324236 | 1.2.0   | 2021-12-23 |  5121  |
| PT04-2 | CAMBRIAN SCHOOL DISTRICT                     | 329264 | 1.2.0   | 2021-12-23 |  8399  |
| PT05-1 | OAKES PUBLIC SCHOOLS                         | 322894 | 1.2.0   | 2021-12-23 | 18435  |
| PT05-2 | DIBUNA UNIFIED SCHOOL DISTRICT               | 326419 | 1.2.3   | 2022-02-18 |  8202  |
| PT06-2 | SOUTH SHORE VOCATIONAL TECHNICAL HIGH SCHOOL | 316930 | 1.2.0   | 2021-12-23 | 13074  |
