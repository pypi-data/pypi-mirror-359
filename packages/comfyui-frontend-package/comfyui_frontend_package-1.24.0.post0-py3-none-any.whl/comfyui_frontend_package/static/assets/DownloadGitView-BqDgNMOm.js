var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });
import { defineComponent, openBlock, createBlock, withCtx, createBaseVNode, toDisplayString, createVNode, unref } from "./vendor-vue-DbSbNqzX.js";
import { script$2 as script } from "./vendor-primevue-CGMNnJS3.js";
import { useRouter } from "./index-Bm0FjBLW.js";
import { _sfc_main as _sfc_main$1 } from "./BaseViewTemplate-Cc7ATWEZ.js";
import "./vendor-vue-i18n-IV1BVZMP.js";
const _hoisted_1 = { class: "max-w-screen-sm flex flex-col gap-8 p-8 bg-[url('/assets/images/Git-Logo-White.svg')] bg-no-repeat bg-right-top bg-origin-padding" };
const _hoisted_2 = { class: "mt-24 text-4xl font-bold text-red-500" };
const _hoisted_3 = { class: "space-y-4" };
const _hoisted_4 = { class: "text-xl" };
const _hoisted_5 = { class: "text-xl" };
const _hoisted_6 = { class: "text-m" };
const _hoisted_7 = { class: "flex gap-4 flex-row-reverse" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "DownloadGitView",
  setup(__props) {
    const openGitDownloads = /* @__PURE__ */ __name(() => {
      window.open("https://git-scm.com/downloads/", "_blank");
    }, "openGitDownloads");
    const skipGit = /* @__PURE__ */ __name(async () => {
      console.warn("pushing");
      const router = useRouter();
      await router.push("install");
    }, "skipGit");
    return (_ctx, _cache) => {
      return openBlock(), createBlock(_sfc_main$1, null, {
        default: withCtx(() => [
          createBaseVNode("div", _hoisted_1, [
            createBaseVNode("h1", _hoisted_2, toDisplayString(_ctx.$t("downloadGit.title")), 1),
            createBaseVNode("div", _hoisted_3, [
              createBaseVNode("p", _hoisted_4, toDisplayString(_ctx.$t("downloadGit.message")), 1),
              createBaseVNode("p", _hoisted_5, toDisplayString(_ctx.$t("downloadGit.instructions")), 1),
              createBaseVNode("p", _hoisted_6, toDisplayString(_ctx.$t("downloadGit.warning")), 1)
            ]),
            createBaseVNode("div", _hoisted_7, [
              createVNode(unref(script), {
                label: _ctx.$t("downloadGit.gitWebsite"),
                icon: "pi pi-external-link",
                "icon-pos": "right",
                severity: "primary",
                onClick: openGitDownloads
              }, null, 8, ["label"]),
              createVNode(unref(script), {
                label: _ctx.$t("downloadGit.skip"),
                icon: "pi pi-exclamation-triangle",
                severity: "secondary",
                onClick: skipGit
              }, null, 8, ["label"])
            ])
          ])
        ]),
        _: 1
      });
    };
  }
});
export {
  _sfc_main as default
};
//# sourceMappingURL=DownloadGitView-BqDgNMOm.js.map
