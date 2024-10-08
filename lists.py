import bpy

# Rename list
namelist = [

("下半身",
"pelvis"),
("上半身",
"spine_01"),
("上半身2",
"spine_02"),
("首",
"neck_01"),
("頭",
"head"),

("足ＩＫ.R",
"ik_foot_r"),
("足ＩＫ.L",
"ik_foot_l"),

("足.L",
"thigh_l"),
("ひざ.L",
"calf_l"),
("足首.L",
"foot_l"),
("足先EX.L",
"ball_l"),

("足.R",
"thigh_r"),
("ひざ.R",
"calf_r"),
("足首.R",
"foot_r"),
("足先EX.R",
"ball_r"),

("肩.L",
"clavicle_l"),
("腕.L",
"upperarm_l"),
("腕捩.L",
"upperarm_twist_01_l"),
("ひじ.L",
"lowerarm_l"),
("手捩.L",
"lowerarm_twist_01_l"),
("手首.L",
"hand_l"),

("肩.R",
"clavicle_r"),
("腕.R",
"upperarm_r"),
("腕捩.R",
"upperarm_twist_01_r"),
("ひじ.R",
"lowerarm_r"),
("手捩.R",
"lowerarm_twist_01_r"),
("手首.R",
"hand_r"),

("親指０.L",
"thumb_01_l"),
("親指１.L",
"thumb_02_l"),
("親指２.L",
"thumb_03_l"),

("人指１.L",
"index_01_l"),
("人指２.L",
"index_02_l"),
("人指３.L",
"index_03_l"),

("中指１.L",
"middle_01_l"),
("中指２.L",
"middle_02_l"),
("中指３.L",
"middle_03_l"),

("薬指１.L",
"ring_01_l"),
("薬指２.L",
"ring_02_l"),
("薬指３.L",
"ring_03_l"),

("小指１.L",
"pinky_01_l"),
("小指２.L",
"pinky_02_l"),
("小指３.L",
"pinky_03_l"),

("親指０.R",
"thumb_01_r"),
("親指１.R",
"thumb_02_r"),
("親指２.R",
"thumb_03_r"),

("人指１.R",
"index_01_r"),
("人指２.R",
"index_02_r"),
("人指３.R",
"index_03_r"),

("中指１.R",
"middle_01_r"),
("中指２.R",
"middle_02_r"),
("中指３.R",
"middle_03_r"),

("薬指１.R",
"ring_01_r"),
("薬指２.R",
"ring_02_r"),
("薬指３.R",
"ring_03_r"),

("小指１.R",
"pinky_01_r"),
("小指２.R",
"pinky_02_r"),
("小指３.R",
"pinky_03_r"),

]

namelist_finger_l = {"index_01_l","index_02_l","index_03_l",
                             "middle_01_l","middle_02_l","middle_03_l",
                             "ring_01_l","ring_02_l","ring_03_l",
                             "pinky_01_l","pinky_02_l","pinky_03_l",}

namelist_finger_r = {"index_01_r","index_02_r","index_03_r",
                             "middle_01_r","middle_02_r","middle_03_r",
                             "ring_01_r","ring_02_r","ring_03_r",
                             "pinky_01_r","pinky_02_r","pinky_03_r",}

# 足D等骨骼列表
namelist_1 = [
("足D.L",
"足.L"),
("ひざD.L",
"ひざ.L"),
("足首D.L",
"足首.L"),

("足D.R",
"足.R"),
("ひざD.R",
"ひざ.R"),
("足首D.R",
"足首.R"),

]

# Reparent List first is child, second is parent
reparent_list = [
("pelvis", "root"),
("ik_foot_root", "root"),
("ik_hand_root", "root"),

('spine_01', 'pelvis'),
('spine_02', 'spine_01'),
('clavicle_l', 'spine_02'),
('upperarm_l', 'clavicle_l'),
('lowerarm_l', 'upperarm_l'),
('hand_l', 'lowerarm_l'),
('index_01_l', 'hand_l'),
('index_02_l', 'index_01_l'),
('index_03_l', 'index_02_l'),
('middle_01_l', 'hand_l'),
('middle_02_l', 'middle_01_l'),
('middle_03_l', 'middle_02_l'),
('pinky_01_l', 'hand_l'),
('pinky_02_l', 'pinky_01_l'),
('pinky_03_l', 'pinky_02_l'),
('ring_01_l', 'hand_l'),
('ring_02_l', 'ring_01_l'),
('ring_03_l', 'ring_02_l'),
('thumb_01_l', 'hand_l'),
('thumb_02_l', 'thumb_01_l'),
('thumb_03_l', 'thumb_02_l'),
('lowerarm_twist_01_l', 'lowerarm_l'),
('upperarm_twist_01_l', 'upperarm_l'),
('clavicle_r', 'spine_02'),
('upperarm_r', 'clavicle_r'),
('lowerarm_r', 'upperarm_r'),
('hand_r', 'lowerarm_r'),
('index_01_r', 'hand_r'),
('index_02_r', 'index_01_r'),
('index_03_r', 'index_02_r'),
('middle_01_r', 'hand_r'),
('middle_02_r', 'middle_01_r'),
('middle_03_r', 'middle_02_r'),
('pinky_01_r', 'hand_r'),
('pinky_02_r', 'pinky_01_r'),
('pinky_03_r', 'pinky_02_r'),
('ring_01_r', 'hand_r'),
('ring_02_r', 'ring_01_r'),
('ring_03_r', 'ring_02_r'),
('thumb_01_r', 'hand_r'),
('thumb_02_r', 'thumb_01_r'),
('thumb_03_r', 'thumb_02_r'),
('lowerarm_twist_01_r', 'lowerarm_r'),
('upperarm_twist_01_r', 'upperarm_r'),
('neck_01', 'spine_02'),
('head', 'neck_01'),
('thigh_l', 'pelvis'),
('calf_l', 'thigh_l'),
('calf_twist_01_l', 'calf_l'),
('foot_l', 'calf_l'),
('ball_l', 'foot_l'),
('thigh_twist_01_l', 'thigh_l'),
('thigh_r', 'pelvis'),
('calf_r', 'thigh_r'),
('calf_twist_01_r', 'calf_r'),
('foot_r', 'calf_r'),
('ball_r', 'foot_r'),
('thigh_twist_01_r', 'thigh_r'),
('ik_foot_l', 'ik_foot_root'),
('ik_foot_r', 'ik_foot_root'),
('ik_hand_gun', 'ik_hand_root'),
('ik_hand_l', 'ik_hand_gun'),
('ik_hand_r', 'ik_hand_gun'),

]

# bones that need to add
bones_add = {
    "ik_foot_root",
    "ik_hand_root",
    "ik_hand_gun",
    "ik_hand_l",
    "ik_hand_r"
}

# bones that ignored to remove

bones_ignore = {
    "ik_foot_l",
    "ik_foot_r",
}

# arm bones
bones_arm_l = {
    "clavicle_l",
    "upperarm_l",
    "upperarm_twist_01_l",
    "lowerarm_l",
    "lowerarm_twist_01_l"
}

bones_arm_r = {
    "clavicle_r",
    "upperarm_r",
    "upperarm_twist_01_r",
    "lowerarm_r",
    "lowerarm_twist_01_r"
}

pose_rot_list = {
    ("upperarm_l", 'Z', 5),
    ("upperarm_r", 'Z', 5),
    ("lowerarm_l", 'Z', -30),
    ("lowerarm_r", 'Z', -30),
    ("hand_l", 'Z', 5),
    ("hand_r", 'Z', 5),
    ("thigh_l", 'Y', -4),
    ("thigh_r", 'Y', -4),
    ("foot_l", 'Y', 4),
    ("foot_r", 'Y', 4),

    ("index_01_l", 'Z', 15),
    ("index_02_l", 'Z', 15),
    ("index_03_l", 'Z', 15),

    ("middle_01_l", 'Z', 15),
    ("middle_02_l", 'Z', 15),
    ("middle_03_l", 'Z', 15),

    ("ring_01_l", 'Z', 15),
    ("ring_02_l", 'Z', 15),
    ("ring_03_l", 'Z', 15),

    ("pinky_01_l", 'Z', 15),
    ("pinky_02_l", 'Z', 15),
    ("pinky_03_l", 'Z', 15),

    ("index_01_r", 'Z', 15),
    ("index_02_r", 'Z', 15),
    ("index_03_r", 'Z', 15),

    ("middle_01_r", 'Z', 15),
    ("middle_02_r", 'Z', 15),
    ("middle_03_r", 'Z', 15),

    ("ring_01_r", 'Z', 15),
    ("ring_02_r", 'Z', 15),
    ("ring_03_r", 'Z', 15),

    ("pinky_01_r", 'Z', 15),
    ("pinky_02_r", 'Z', 15),
    ("pinky_03_r", 'Z', 15),
}

spine_rot_list = {
    ("pelvis", 'X', 90),
    ("pelvis", 'Y', -90),
    ("spine_01", 'X', -90),
    ("spine_01", 'Y', -90),
    ("spine_02", 'X', -90),
    ("spine_02", 'Y', -90),
    ("neck_01", 'X', -90),
    ("neck_01", 'Y', -90),
    ("head", 'X', -90),
    ("head", 'Y', -90)
}