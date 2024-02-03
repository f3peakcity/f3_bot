CREATE OR REPLACE VIEW backblast_greenlevel as (
    SELECT * from backblast where team_id = 'T04GS2ZJBHD'
);

CREATE OR REPLACE VIEW backblast_churham as (
    SELECT * from backblast where team_id = 'T4GNGR79U'
);

CREATE OR REPLACE VIEW backblast_peakcity as (
    SELECT * from backblast where team_id = 'T046M8F12U8'
);
