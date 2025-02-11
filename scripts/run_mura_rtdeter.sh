model_name=rtdetr # 可修改，如 yolov7
job_name=rtdetr_r18vd_6x_coco # 可修改，如 yolov7_tiny_300e_coco
project_name=Mura
config=configs/${project_name}/${model_name}/${job_name}.yml
log_dir=log_dir/${job_name}
#weights=https://bj.bcebos.com/v1/paddledet/models/${job_name}.pdparams
#weights=output/${job_name}/model_final.pdparams

# 1.训练（单卡/多卡），加 --eval 表示边训边评估，加 --amp 表示混合精度训练
CUDA_VISIBLE_DEVICES=6 python tools/train.py -c ${config} --eval --vdl_log_dir vdl_log_dir/${job_name}
#python -m paddle.distributed.launch --log_dir=${log_dir} --gpus 4,5,6,7 tools/train.py -c ${config} --eval

# 2.评估，加 --classwise 表示输出每一类mAP
#CUDA_VISIBLE_DEVICES=0 python tools/eval.py -c ${config} -o weights=${weights} --classwise

# 3.预测 (单张图/图片文件夹）
#CUDA_VISIBLE_DEVICES=0 python tools/infer.py -c ${config} -o weights=${weights} --infer_img=demo/000000014439_640x640.jpg --draw_threshold=0.5
#CUDA_VISIBLE_DEVICES=0 python tools/infer.py -c ${config} -o weights=${weights} --infer_dir=demo/ --draw_threshold=0.5