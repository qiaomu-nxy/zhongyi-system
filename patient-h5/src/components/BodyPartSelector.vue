<template>
  <div class="body-selector">
    <svg viewBox="0 0 200 400" class="body-svg" @click="handleClick">
      <!-- 头 -->
      <ellipse cx="100" cy="36" rx="28" ry="32" :class="cls('头部')" data-part="头部" />
      <!-- 面部(眼睛区域) -->
      <ellipse cx="100" cy="52" rx="18" ry="10" :class="cls('面部')" data-part="面部" />
      <!-- 颈 -->
      <rect x="88" y="68" width="24" height="18" rx="6" :class="cls('颈部')" data-part="颈部" />
      <!-- 肩左右 -->
      <ellipse cx="58" cy="96" rx="22" ry="14" :class="cls('肩部')" data-part="肩部" />
      <ellipse cx="142" cy="96" rx="22" ry="14" :class="cls('肩部')" data-part="肩部" />
      <!-- 胸 -->
      <rect x="72" y="86" width="56" height="54" rx="8" :class="cls('胸部')" data-part="胸部" />
      <!-- 腹 -->
      <rect x="74" y="140" width="52" height="44" rx="8" :class="cls('腹部')" data-part="腹部" />
      <!-- 腰 -->
      <rect x="76" y="184" width="48" height="28" rx="8" :class="cls('腰部')" data-part="腰部" />
      <!-- 背(用不同色区分，覆盖胸腹区域偏后——前视图中标注在侧面) -->
      <rect x="156" y="90" width="30" height="80" rx="8" :class="cls('背部')" data-part="背部" />
      <!-- 上肢 -->
      <rect x="28" y="110" width="20" height="80" rx="8" :class="cls('上肢')" data-part="上肢" />
      <rect x="152" y="110" width="20" height="80" rx="8" :class="cls('上肢')" data-part="上肢" />
      <!-- 下肢 -->
      <rect x="78" y="214" width="20" height="100" rx="8" :class="cls('下肢')" data-part="下肢" />
      <rect x="102" y="214" width="20" height="100" rx="8" :class="cls('下肢')" data-part="下肢" />
      <!-- 足部 -->
      <ellipse cx="88" cy="328" rx="14" ry="10" :class="cls('足部')" data-part="足部" />
      <ellipse cx="112" cy="328" rx="14" ry="10" :class="cls('足部')" data-part="足部" />
      <!-- 全身 (文字标注区) -->
      <rect x="6" y="340" width="60" height="28" rx="8" :class="cls('全身')" data-part="全身" />
      <text x="36" y="359" text-anchor="middle" font-size="11" fill="currentColor" pointer-events="none">全身</text>
    </svg>

    <div class="selected-tags">
      <van-tag
        v-for="p in modelValue"
        :key="p"
        closeable
        type="warning"
        size="medium"
        @close="remove(p)"
        class="sel-tag"
      >{{ p }}</van-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: string[] }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: string[]): void }>()

function cls(part: string) {
  return ['body-part', props.modelValue.includes(part) ? 'selected' : '']
}

function handleClick(e: MouseEvent) {
  const el = e.target as SVGElement
  const part = el.dataset.part
  if (!part) return
  const list = [...props.modelValue]
  const idx = list.indexOf(part)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(part)
  emit('update:modelValue', list)
}

function remove(part: string) {
  emit('update:modelValue', props.modelValue.filter(p => p !== part))
}
</script>

<style scoped>
.body-selector { display: flex; flex-direction: column; align-items: center; }
.body-svg { width: 180px; height: 360px; }
.body-part {
  fill: #e8f5e9;
  stroke: #bdbdbd;
  stroke-width: 1.5;
  cursor: pointer;
  transition: fill .2s, stroke .2s;
}
.body-part.selected {
  fill: #FFEBEE;
  stroke: #EF9A9A;
  stroke-width: 2.5;
}
.body-part:hover { opacity: 0.8; }
.selected-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; justify-content: center; }
.sel-tag { --van-tag-warning-color: #EF9A9A; }
</style>