call traffictrackergui-env/Scripts/activate

echo ====================================================
echo ================= Build box_utils ==================
echo ====================================================
cd D:\UAV_traffic_conflict_analysis\TrafficTrackerGUI-MOTC\Model\YOLOv4\utils_pkg\box_utils_win
python setup_win.py -v build_ext --inplace

pause