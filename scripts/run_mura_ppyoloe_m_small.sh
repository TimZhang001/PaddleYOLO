model_name=ppyoloe # 可修改，如 yolov7
job_name=ppyoloe_plus_crn_m_80e_mura_small # 可修改，如 yolov7_tiny_300e_coco
config=project/${model_name}/${job_name}.yml
log_dir=log_dir/${job_name}

# 1.训练（单卡/多卡），加 --eval 表示边训边评估，加 --amp 表示混合精度训练
CUDA_VISIBLE_DEVICES=4 python tools/train.py -c ${config} --eval --amp --vdl_log_dir vdl_log_dir/${job_name}

# 2.评估，加 --classwise 表示输出每一类mAP
#CUDA_VISIBLE_DEVICES=7 python tools/eval.py -c ${config} --classwise

# 3.预测 (单张图/图片文件夹）
#CUDA_VISIBLE_DEVICES=0 python tools/infer.py -c ${config} -o weights=${weights} --infer_img=demo/000000014439_640x640.jpg --draw_threshold=0.5

# 4. 导出模型
#CUDA_VISIBLE_DEVICES=7 python tools/export_model.py -c ${config} 